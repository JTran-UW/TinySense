# -*- coding: utf-8 -*-
"""
Created on Sun Jun 23 00:29:13 2024

@author: zhita
"""

import pandas as pd
from math import radians
import numpy as np
from scipy import signal
from scipy.spatial.transform import Rotation
import control
from sklearn.metrics import root_mean_squared_error

def find_max_pz_timestamp(df):
    
    max_idx = df["pz(m)"].idxmax()
    max_timestamp = df.loc[max_idx, "timestamp"]
    
    return max_timestamp

def preprocess_data(cf_path, ts_path, mocap_path, experiment_num):
    
    """Preprocess data from Crazyflie, TinySense, and Mocap systems."""
    # Load data
    cf_data = pd.read_csv(cf_path, header=0)
    ts_data = pd.read_csv(ts_path, header=0)
    mocap_data = pd.read_csv(mocap_path, header=0)

    # Print data info
    print(f'TinySense data length: {len(ts_data)}')
    print(f'TinySense info:\n{ts_data.info()}')
    print(f'Crazyflie data length: {len(cf_data)}')
    print(f'Crazyflie info:\n{cf_data.info()}')

    # Process mocap data
    mocap_data.drop("header.frame_id", axis=1, inplace=True)
    ts_data.rename(columns={ts_data.columns[0]: 'timestamp'}, inplace=True)
    mocap_data.rename(columns={mocap_data.columns[0]: 'timestamp'}, inplace=True)

    # Convert and scale units
    ts_data["gyro(d/s)"] = ts_data.apply(lambda row: -radians(row["gyro(d/s)"]), axis=1)
    cf_data["gyro_pitch_filtered(rad/s)"] = cf_data.apply(lambda row: radians(row["gyro_pitch_filtered(rad/s)"]), axis=1)
    ts_data["optic_flow(rad/s)"] *= -1.2  # Apply scaling factor

    # Subtract z-bias for TinySense
    z_bias = ts_data["z(m)"].iloc[:5].mean()
    ts_data["z(m)"] = ts_data["z(m)"] - z_bias

    # Subtract gyro bias for TinySense and Crazyflie
    gyro_bias_tiny = ts_data["gyro(d/s)"].iloc[:5].mean()
    ts_data["gyro(d/s)"] = ts_data["gyro(d/s)"] - gyro_bias_tiny
    gyro_bias_crazyflie = cf_data["gyro_pitch_filtered(rad/s)"].iloc[:5].mean()
    cf_data["gyro_pitch_filtered(rad/s)"] = cf_data["gyro_pitch_filtered(rad/s)"] - gyro_bias_crazyflie

    # Time filtering based on max pz timestamp
    max_time = find_max_pz_timestamp(cf_data)
    TIME_LOWER_BOUND = max_time - 7
    TIME_UPPER_BOUND = cf_data["timestamp"].iloc[-1]

    # Filter data based on time range
    ts_data = ts_data[(ts_data.timestamp > TIME_LOWER_BOUND) & (ts_data.timestamp <= TIME_UPPER_BOUND)]
    cf_data = cf_data[(cf_data.timestamp > TIME_LOWER_BOUND) & (cf_data.timestamp <= TIME_UPPER_BOUND)]
    mocap_data = mocap_data[(mocap_data.timestamp > TIME_LOWER_BOUND) & (mocap_data.timestamp <= TIME_UPPER_BOUND)]

    # Shift the timestamps for all datasets
    ts_data["timestamp"] -= ts_data["timestamp"].iloc[0]
    cf_data["timestamp"] -= cf_data["timestamp"].iloc[0]
    mocap_data["timestamp"] -= mocap_data["timestamp"].iloc[0]

    # Further shift to align with propeller start time (approx. 0.5s)
    time_shift = 0.5
    ts_data["timestamp"] -= ts_data["timestamp"].iloc[(ts_data["timestamp"] - time_shift).abs().argmin()]
    cf_data["timestamp"] -= cf_data["timestamp"].iloc[(cf_data["timestamp"] - time_shift).abs().argmin()]
    mocap_data["timestamp"] -= mocap_data["timestamp"].iloc[(mocap_data["timestamp"] - time_shift).abs().argmin()]

    # Adjust z bias for experiment 0
    if experiment_num == 0:
        z_bias_ts = ts_data["z(m)"].iloc[:5].mean()
        ts_data.loc[ts_data["timestamp"] > 0, "z(m)"] = ts_data.loc[ts_data["timestamp"] > 0, "z(m)"] - z_bias_ts + 0.2

    return cf_data, ts_data, mocap_data


def interpolate_mocap(mocap_data):
    """Interpolates mocap data to obtain velocity, angle, and altitude."""
    mocap_interp_time = np.linspace(mocap_data.iloc[0]["timestamp"], mocap_data.iloc[-1]["timestamp"], len(mocap_data))
    mocap_interp_px = np.interp(mocap_interp_time, mocap_data["timestamp"], mocap_data["pose.position.y"])

    # Apply a low-pass filter to the interpolated position data
    b, a = signal.butter(2, 0.1)
    mocap_interp_px = signal.filtfilt(b, a, mocap_interp_px)

    # Calculate velocity (vx)
    mocap_interp_vx = np.gradient(mocap_interp_px, mocap_interp_time)

    # Calculate pitch angle (theta)
    quats = [Rotation.from_quat([row["pose.orientation.x"], row["pose.orientation.y"], row["pose.orientation.z"], row["pose.orientation.w"]]) for _, row in mocap_data.iterrows()]
    bias = quats[0].as_euler("xyz")[0]
    mocap_interp_theta = np.interp(mocap_interp_time, mocap_data["timestamp"], [-q.as_euler("xyz")[0] + bias for q in quats])
    mocap_interp_theta = signal.filtfilt(b, a, mocap_interp_theta)

    # Interpolate altitude (z)
    mocap_interp_z = np.interp(mocap_interp_time, mocap_data["timestamp"], mocap_data["pose.position.z"])
    mocap_interp_z = signal.filtfilt(b, a, mocap_interp_z)

    return pd.DataFrame({"timestamp": mocap_interp_time, "vx(m/s)": mocap_interp_vx, "theta": mocap_interp_theta, "z(m)": mocap_interp_z})




def kalman_filter_optimal_pure_tinysense(cf_data_df, ts_data_df, mocap_data_df, G, Q, R):
    """Performs Kalman filtering with z set to 0.01m and optic flow to 0 before 1.8 seconds."""
    b = 13.2e-3
    m = 0.3
    zd = 1  # Desired altitude

    A = np.array([[0, 0, 0],
                  [-9.81, -b/m, 0],
                  [0, 0, 0]])

    B = np.array([[1, 0, 0]]).T
    C = np.array([[0, -1/zd, 0],
                  [0, 0, 1]])
    D = np.array([[1, 0]]).T

 #    # Parameters for Kalman filter
 #    # params = np.array([0.72, 0.10, 20.00, 0.14, 0.093, 0.08, 1.06, 0.20])
 #    # params = np.array([1.00, 1.00, 1.00, 0.1008, 0.0093, 1.60, 1.06, 0.20])
 #    # params = np.array([1.00, 1.00, 1.00, 0.09671361,  0.09517281, 29.96929001,  1.05259944, 10.09166303 ])
    
 #    params = np.array([1.00, 1.00, 1.00, 2.49437107,  0.12233922, 30,  6.47308048, 10])
    
 # #    #new trying of the gradient descent
 # #    params = np.array([0.93446281, 0.99503374, 1, 0.04641337, 0.01005693, 0.8,
 # # 0.88154469, 0.2])
    
 #    G = np.diag(params[:3])
 #    Q = np.diag(params[3:6] ** 2)
 #    R = np.diag(params[6:] ** 2)

    L, _, _ = control.lqe(A, G, C, Q, R)

    # Ignore pressure sensor and optic flow data before 1.8s
    ts_data_df.loc[ts_data_df["timestamp"] < 1.8, ["z(m)", "optic_flow(rad/s)"]] = [0.01, 0]

    ts_data = ts_data_df.to_numpy(dtype="float64", copy=True)
    cf_data = cf_data_df.to_numpy(dtype="float64")
    mocap_data = mocap_data_df.to_numpy(dtype="float64")

    # Find indices for zero-time points
    zero_idx_cf = np.where(cf_data[:, 0] == 0)[0][0]
    zero_idx_ts = np.where(ts_data[:, 0] == 0)[0][0]
    zero_idx_mocap = np.argmin(np.abs(mocap_data[:, 0]))

    q_est = np.zeros([ts_data.shape[0], 3])
    q_est[zero_idx_ts] = [-cf_data[zero_idx_cf, 6], -cf_data[zero_idx_cf, 5], 0.08]

    for i in range(zero_idx_ts + 1, ts_data.shape[0]):
        y = ts_data[i - 1, [1, 3]].reshape([2, 1])
        u = ts_data[i - 1, 2].reshape([1, 1])

        if ts_data[i, 0] == ts_data[i - 1, 0]:
            ts_data[i, 0] = (ts_data[i - 1, 0] + ts_data[i + 1, 0]) / 2

        dt = ts_data[i, 0] - ts_data[i - 1, 0]
        qhat = q_est[i - 1, :].reshape([3, 1])
        qdot = A @ qhat + B @ u + L @ (y - C @ qhat - D @ u)
        q_est[i, :] = (qhat + dt * qdot).reshape([3,])

    # Concatenate the time column with the estimated states
    ts_first_column = ts_data[:, 0].reshape(-1, 1)
    q_est = np.concatenate((ts_first_column, q_est), axis=1)

    # print(f"Length of Crazyflie data: {len(cf_data)}")
    # print(f"Length of estimated data: {len(q_est)}")

    return cf_data, ts_data, mocap_data, q_est, zero_idx_ts, zero_idx_cf, zero_idx_mocap, L





# def kalman_filter_optimal_crazyflie(cf_data_df, ts_data_df, G, Q, R):
#     b = 13.2 * (10 ** (-3))
#     m = 0.3  # Mass
#     zd = 1 # Desired altitude
    
#     A = np.array([[0,     0,    0],
#                   [-9.81, -b/m, 0],
#                   [0,     0,    0]])
    
#     B = np.array([[1, 0, 0]]).T
    
#     C = np.array([[0, -1/zd, 0],
#                   [0, 0,     1]])
    
#     D = np.array([[1, 0]]).T
    
    # G = np.array([[1, 0, 0 ],
    #               [0, 1, 0 ],
    #               [0, 0, 20]])
    
    # Q = np.array([[0.01 ** 2, 0,        0       ],
    #               [0,         0.1 ** 2, 0       ],
    #               [0,         0,        0.08 ** 2]])
    
    # # Q = np.array([[0.08 ** 2, 0,        0       ],
    # #           [0,         0.001 ** 2, 0       ],
    # #           [0,         0,        1 ** 2]])
    
    # R = np.array([[0.8 ** 2, 0        ],
    #               [0,         0.2 ** 2]])
    
    
    # # G = np.array([[1, 0, 0 ],
    # #               [0, 1, 0 ],
    # #               [0, 0, 20]])
    
    # # Q = np.array([[8 ** 2, 0,        0       ],
    # #               [0,         0.1 ** 2, 0       ],
    # #               [0,         0,        0.08 ** 2]])
    
    # # # Q = np.array([[0.08 ** 2, 0,        0       ],
    # # #           [0,         0.001 ** 2, 0       ],
    # # #           [0,         0,        1 ** 2]])
    
    # # R = np.array([[20 ** 2, 0        ],
    # #               [0,         0.2 ** 2]])
    
    # L, _, _ = control.lqe(A, G, C, Q, R)
    
    # # print(ts_data_df.info())
    # ts_data = ts_data_df.to_numpy(dtype="float64", copy=True)
    # cf_data = cf_data_df.to_numpy(dtype="float64")
    # # mocap_data = mocap_data_df.to_numpy(dtype="float64")
    
    # q_est = np.zeros([ts_data.shape[0], 3])
    # q_est[0] = [-cf_data[0, 6], # Theta
    #             -cf_data[0, 5], # Vx
    #             cf_data[0, 3]] # Z
    
    # for i in range(1, ts_data.shape[0]):
    #     # print('ts has the length', len(ts_data))
        
    #     # print('cf has the length', len(cf_data))
    #     y = ts_data[i-1, [1, 3]].reshape([2, 1])
        
    #     # try crazyflie optic flow
    #     y = np.zeros([2,1])
    #     crazyflie_of = cf_data[i-1, 10]
    #     y[0] = crazyflie_of
    #     crazyflie_z = cf_data[i-1, 3]
    #     y[1] = crazyflie_z
        
    #     # u = ts_data[i-1, 2].reshape([1, 1])
    #     u = cf_data[i-1, 8].reshape([1, 1])  # use crazyflie gyro.
    #     if ts_data[i, 0] == ts_data[i - 1, 0]:
    #         ts_data[i, 0] = (ts_data[i - 1, 0] + ts_data[i + 1, 0]) / 2
    #     dt = ts_data[i, 0] - ts_data[i - 1, 0]
    #     qhat = q_est[i-1, :].reshape([3, 1])
    #     qdot = A @ qhat + B @ u + L @ (y - C @ qhat - D @ u)
    #     q_est[i, :] = (qhat + dt*qdot).reshape([3,])
    
    # return cf_data, ts_data, q_est
    