
"""
Created on FEB 19

Ninja Robot Thesis

@author: Mohamad Sayegh

MPC 

using path parameters


        
"""


import numpy as np
from numpy import pi, cos, sin
import matplotlib.pyplot as plt
from scipy import interpolate
from pylab import *
from casadi import Function, linspace, vertcat, horzcat, DM, interpolant, sum1, MX, hcat, sumsqr
from rockit import *
from rockit import Ocp , FreeTime, MultipleShooting
from MPC_Bubble_tunnel_generation_v2 import generate_bubbles_mpc_v3, plotting, get_bubbles_mpc_loop
from MPC_Grid_generation import create_obstacles_mpc, create_global_path_mpc
from Bubble_tunnel_generation_v2 import create_tunnel, plotting_v2, find_path







obstacles_option  = 1
path_option       = 1


global_end_goal_x       =    9     #position of initial and end point
global_end_goal_y       =    9
initial_pos_x           =    0
initial_pos_y           =    0
xlim_min                =   -2     #xlim and ylim of plotsR
xlim_max                =    12
ylim_min                =   -2
ylim_max                =    12

   

obs_horizon       = 1000
path_horizon      = 1    
 
N       = 5
dt      = 2            
Nsim    = 20

#------------- Initialize OCP

ocp = Ocp(T = N*dt)       



#---------------- Initialize grid, occupied positions and bubbles

occupied_positions_x , occupied_positions_y = create_obstacles_mpc(obstacles_option,initial_pos_x,initial_pos_y,obs_horizon)

global_path_x, global_path_y, Bspline_obj   = create_global_path_mpc(path_option,initial_pos_x,initial_pos_y,path_horizon, N)

midpointx, midpointy, radiusx, radiusy = generate_bubbles_mpc_v3(global_path_x, global_path_y,occupied_positions_x,occupied_positions_y)
    

global_path_x, global_path_y, index = find_path(global_path_x, global_path_y, midpointx , midpointy , radiusx ,radiusy, N)    
        


# ----------- draw ellipse
npoints =  500  #numbr of points of every circle
ts      =  np.linspace(0, 2*np.pi, npoints) #for creating circles points


ellipse_x =  midpointx + radiusx*cos(ts) 
ellipse_y =  midpointy + radiusy*sin(ts)  


plt.figure(dpi=300)
plt.xlabel('x [m]')
plt.ylabel('y [m]')
plt.xlim([xlim_min,xlim_max])
plt.ylim([ylim_min,ylim_max])
plt.plot(global_path_x, global_path_y, 'g--')
plt.plot(midpointx, midpointy,'bx')
plt.plot(ellipse_x,ellipse_y,'b.', markersize = 1)
plt.plot(occupied_positions_x,occupied_positions_y,'bo',markersize = 1)
plt.legend(['original path','Obstacles', 'Feasible tunnel', 'OCP solution'])
plt.title('OCP Solutin with given path and tunnel')
plt.xlabel('x [m]')
plt.ylabel('y [m]')
plt.savefig('OCP Solution', dpi=300)
plt.pause(0.01)



#------------------------- System model

x       =  ocp.state()
y       =  ocp.state()
theta   =  ocp.state()
v       =  ocp.control()
w       =  ocp.control()

#--------------------------path parameters 

s_path       =  ocp.state()
sdot_path    =  ocp.control()

#-----------------------------ODEs

ocp.set_der(x            ,        v*cos(theta))
ocp.set_der(y            ,        v*sin(theta))
ocp.set_der(theta        ,        w)
ocp.set_der(s_path       ,        sdot_path)


#-------------------------------------------------------------------------------#
#                            Solve the first iteration                          #
#-------------------------------------------------------------------------------#


#------------------------- Constraints on initial and end point


X_0  = ocp.parameter(4)
X    = vertcat(x, y, theta, s_path)

ocp.subject_to(ocp.at_t0(X) == X_0)

current_X = vertcat(initial_pos_x,initial_pos_y,0.0,0.0) 

ocp.set_value(X_0, current_X)



global_goal = vertcat(global_end_goal_x,global_end_goal_y)


end_goal_x = ocp.parameter(1)
end_goal_y = ocp.parameter(1)

ocp.set_value( end_goal_x, global_path_x[-1])
ocp.set_value( end_goal_y, global_path_y[-1])



#----------------------------- constraints on controls 

ocp.subject_to(  0          <= ( v  <= 1   ))
ocp.subject_to( -pi         <= ( w  <= pi  ))

ocp.subject_to( sdot_path   >=   0)        



#---------------------- Obscatles avoidance 


bubble_x          =  ocp.parameter(1)
bubble_y          =  ocp.parameter(1)
bubble_radius_x   =  ocp.parameter(1)
bubble_radius_y   =  ocp.parameter(1)

ocp.set_value(bubble_x,          midpointx)
ocp.set_value(bubble_y,          midpointx)
ocp.set_value(bubble_radius_x,   radiusx)
ocp.set_value(bubble_radius_y,   radiusy)


ocp.subject_to( ( (x-bubble_x)**2/bubble_radius_x**2 + (y - bubble_y)**2/bubble_radius_y**2 )  <= 1 )


#---------------------------------- Path Tunnel avoidance 


path_x          =  ocp.parameter(1, grid = 'control')
path_y          =  ocp.parameter(1, grid = 'control')

ocp.set_value(path_x, global_path_x)
ocp.set_value(path_y, global_path_y)


tlength2       =  len(global_path_x)
tunnel_s2      =  np.linspace(0,1,tlength2) 

ocp.subject_to(ocp.at_tf(s_path) == 1)


path_spline_x = interpolant('x','bspline', [tunnel_s2], 1   , {"algorithm": "smooth_linear","smooth_linear_frac":0.49})
path_spline_y = interpolant('y','bspline', [tunnel_s2], 1   , {"algorithm": "smooth_linear","smooth_linear_frac":0.49})


# -------------------------------- Initial guess 


#path parameters
s_guess = np.linspace(0,1,N)

ocp.set_initial(s_path,  s_guess)

sdot_guess = (s_guess[1]-s_guess[0])/dt

ocp.set_initial(sdot_path, sdot_guess)

v_guess = np.ones(N)
w_guess = np.ones(N)

ocp.set_initial(v , v_guess)
ocp.set_initial(w , w_guess)

ocp.set_initial(x,       global_path_x) 
ocp.set_initial(y,       global_path_y) 

# 


# -------------------------------------- Objective function 

#path following

ocp.add_objective( 1*ocp.integral((x - path_spline_x(s_path, path_x))**2 + (y-path_spline_y(s_path,path_y))**2))   

ocp.add_objective( 100*ocp.at_tf(s_path) )
 

# ----------------- Solver

options = {"ipopt": {"print_level": 0}}
options["expand"] = False
options["print_time"] = True
ocp.solver('ipopt', options)


# Multiple shooting
ocp.method(MultipleShooting(N=N,M=2,intg='rk'))


#-------------------------------- OCP Solution and Results                             


try:
    sol = ocp.solve()
except:
    #failed_to_converge = True
    ocp.show_infeasibilities(1e-6)
    sol = ocp.non_converged_solution





#-------------------------------------------------------------------------------#
#                                   MPC                                         #
#-------------------------------------------------------------------------------#


# Get discretised dynamics as CasADi function to simulate the system
Sim_system_dyn = ocp._method.discrete_system(ocp)

# Log data for post-processing  
t_sol, x_sol            = sol.sample(x,           grid='control')
t_sol, y_sol            = sol.sample(y,           grid='control')
t_sol, theta_sol        = sol.sample(theta,       grid='control')
t_sol, s_path_sol       = sol.sample(s_path,      grid='control')
t_sol, v_sol            = sol.sample(v,           grid='control')
t_sol, w_sol            = sol.sample(w,           grid='control')
t_sol, sdot_path_sol    = sol.sample(sdot_path,   grid='control')


t_sol_ref, x_sol_ref        = sol.sample(x,           grid='integrator', refine = 10)
t_sol_ref, y_sol_ref        = sol.sample(y,           grid='integrator', refine = 10)




#------------------ Plotting with respect to initial path/bubbles


# plt.figure(dpi=300)
# plt.xlabel('x [m]')
# plt.ylabel('y [m]')
# plt.xlim([xlim_min,xlim_max])
# plt.ylim([ylim_min,ylim_max])
# plt.plot(global_path[0], global_path[1], 'g--')
# plt.plot(occupied_positions_x,occupied_positions_y,'bo',markersize = 1)
# plt.plot(ellipse_x, ellipse_y, 'g.', markersize= 0.2)
# plt.plot(x_sol, y_sol,'bo', markersize = 5)
# plt.legend(['original path','Obstacles', 'Feasible tunnel', 'OCP solution'])
# plt.title('OCP Solutin with given path and tunnel')
# plt.xlabel('x [m]')
# plt.ylabel('y [m]')
# plt.savefig('OCP Solution', dpi=300)




#--------------------- MPC 

#---------------- Initialize Logging variables

time_hist           = np.zeros((Nsim+1, N+1))
x_hist              = np.zeros((Nsim+1, N+1))
y_hist              = np.zeros((Nsim+1, N+1))
theta_hist          = np.zeros((Nsim+1, N+1))
s_path_hist         = np.zeros((Nsim+1, N+1))
s_obs_hist          = np.zeros((Nsim+1, N+1))
v_hist              = np.zeros((Nsim+1, N+1))
w_hist              = np.zeros((Nsim+1, N+1))
sdot_path_hist      = np.zeros((Nsim+1, N+1))
sdot_obs_hist       = np.zeros((Nsim+1, N+1))


# for post processing
time_hist[0,:]          = t_sol
x_hist[0,:]             = x_sol
y_hist[0,:]             = y_sol
theta_hist[0,:]         = theta_sol
s_path_hist[0,:]        = s_path_sol
v_hist[0,:]             = v_sol
w_hist[0,:]             = w_sol
sdot_path_hist[0,:]     = sdot_path_sol


clearance = 0.2

    
i = 0
    
time = 0 
    
for i in range(Nsim):
    
    
    print("timestep", i+1, "of", Nsim)
    
    
    #------------------- Update initial position ------------------------------
    
    # Combine control inputs
    current_U = vertcat(v_sol[0], w_sol[0] , sdot_path_sol[0])

    # Simulate dynamics (applying the first control input) and update the current state
    current_X = Sim_system_dyn(x0=current_X, u=current_U, T=t_sol[1]-t_sol[0])["xf"]
    
    print( f' x: {current_X[0]}' )
    print( f' y: {current_X[1]}' )
    # print( f' theta: {current_X[2]}' )
    
    initial_pos_x = double(current_X[0])
    initial_pos_y = double(current_X[1])
    
    #------------ Update time spent to reach goal 
    
    time = time + (t_sol[1]-t_sol[0])
   
    #------------------------- Generate grid and path -------------------------

    global_path_x, global_path_y, Bspline_obj = create_global_path_mpc(path_option,initial_pos_x,initial_pos_y,path_horizon, N)
    

    #----------------- get obstacles ------------------------------------------
    
    occupied_positions_x , occupied_positions_y = create_obstacles_mpc(obstacles_option,initial_pos_x,initial_pos_y,obs_horizon)
    
    #---------------- Creating the Bubbles-------------------------------------


    midpoints_x, midpoints_y, radii_x, radii_y = generate_bubbles_mpc_v3(global_path_x, global_path_y,occupied_positions_x,occupied_positions_y)
      
    
    # --------------- select N points for path spline-------------------------

    global_path_x, global_path_y, index = find_path(global_path_x, global_path_y, midpointx , midpointy , radiusx ,radiusy, N)    
        

    #------------------- Updating Tunnels ------------------------------------


    ocp.set_value(path_x, global_path_x)
    ocp.set_value(path_y, global_path_y)
    
    ocp.set_value(bubble_x,          midpointx)
    ocp.set_value(bubble_y,          midpointx)
    ocp.set_value(bubble_radius_x,   radiusx)
    ocp.set_value(bubble_radius_y,   radiusy)
    
    ocp.set_value( end_goal_x, global_path_x[-1])
    ocp.set_value( end_goal_y, global_path_y[-1])

    #initial guess
    ocp.set_initial(x,       global_path_x) 
    ocp.set_initial(y,       global_path_y) 
    
    ocp.set_initial(s_path,  s_guess)
    ocp.set_initial(sdot_path, sdot_path_sol)
    
    ocp.set_initial(v , v_sol)
    ocp.set_initial(w , w_sol)

    
    #----------------  Simulate dynamic system --------------------------------
    

    
    error = sumsqr(current_X[0:2] - global_goal)
    if error < clearance: 
        break   #solution reached the global end goal 
    
    # Set the parameter X0 to the new current_X
    ocp.set_value(X_0, current_X)
    


    #------------------------ Plot results every iteration


    ellipse_x =  midpointx + radiusx*cos(ts) 
    ellipse_y =  midpointy + radiusy*sin(ts)  


    plt.figure(dpi=300)
    plt.title('MPC')    
    plt.plot(x_sol_ref, y_sol_ref, 'b-')
    plt.plot(ellipse_x,ellipse_y,'b.', markersize = 1)
    plt.plot(occupied_positions_x,occupied_positions_y,'co',markersize = 1.5)
    plt.plot(global_path_x, global_path_y, 'g--')
    plt.plot(global_path_x[-1], global_path_y[-1], 'go')
    plt.plot(x_hist[0:i,0],y_hist[0:i,0], 'bo', markersize = 5)
    plt.plot(x_sol[0], y_sol[0], 'bo', markersize = 5)
    plt.xlim([xlim_min,xlim_max])
    plt.ylim([ylim_min,ylim_max])
    plt.pause(0.001)

    
    #------------------------- Solve the optimization problem

    try:
        sol = ocp.solve()
    except:
        #failed_to_converge = True
        ocp.show_infeasibilities(1e-6)
        sol = ocp.non_converged_solution

    #-------------------------- Log data for next iteration  
    
    t_sol, x_sol            = sol.sample(x,           grid='control')
    t_sol, y_sol            = sol.sample(y,           grid='control')
    t_sol, theta_sol        = sol.sample(theta,       grid='control')
    t_sol, s_path_sol       = sol.sample(s_path,      grid='control')
    t_sol, v_sol            = sol.sample(v,           grid='control')
    t_sol, w_sol            = sol.sample(w,           grid='control')
    t_sol, sdot_path_sol    = sol.sample(sdot_path,   grid='control')
 
    t_sol_ref, x_sol_ref        = sol.sample(x,           grid='integrator', refine = 20)
    t_sol_ref, y_sol_ref        = sol.sample(y,           grid='integrator', refine = 20)

    # for post processing
    time_hist[i+1,:]          = t_sol
    x_hist[i+1,:]             = x_sol
    y_hist[i+1,:]             = y_sol
    theta_hist[i+1,:]         = theta_sol
    s_path_hist[i+1,:]        = s_path_sol
    v_hist[i+1,:]             = v_sol
    w_hist[i+1,:]             = w_sol
    sdot_path_hist[i+1,:]     = sdot_path_sol
    


    

# -------------------------------------------
#          Plot the results
# -------------------------------------------

# #global path from initial to end point
# global_path_x, global_path_y, Bspline_obj = create_global_path_mpc(path_option,0,0,1000,50)
# occupied_positions_x , occupied_positions_y = create_obstacles_mpc(obstacles_option,initial_pos_x,initial_pos_y,100)
# shifted_midpoints_x, shifted_midpoints_y, shifted_radii = generate_bubbles_mpc_v2(global_path_x, global_path_y,occupied_positions_x,occupied_positions_y)   
# tunnel_x, tunnel_y = create_tunnel(shifted_midpoints_x,shifted_midpoints_y,shifted_radii)
       

# fig = plt.figure(dpi=300)
# ax2 = plt.subplot(1, 1, 1)
# ax2.plot(global_path[0], global_path[1], '--')
# plt.plot(occupied_positions_x,occupied_positions_y,'ko',markersize = 2)
# ax2.plot(x_hist[0,0], y_hist[0,0], 'b-')
# ax2.set_xlabel('x pos [m]')
# ax2.set_ylabel('y pos [m]')
# ax2.set_title('Interations of OCP solutions')
# ax2.plot(x_hist[0:i,0], y_hist[0:i,0], 'ro')  
# for k in range(i):
#     # ax2.plot(x_hist[k,:], y_hist[k,:], 'b-')
#     ax2.plot(x_hist[k,:], y_hist[k,:], 'g.')  
# plt.savefig('MPC solution with all ocp iterations', dpi=300)



# plt.figure(dpi=300)
# plt.plot(x_hist[0:i,0],y_hist[0:i,0], 'bo', markersize = 5)
# plt.plot(x_hist[0:i,0],y_hist[0:i,0], 'b-', markersize = 5)
# plt.plot(8.8,9,'bo', markersize = 10)
# plt.plot(global_path_x, global_path_y, 'g--')
# plt.plot(occupied_positions_x,occupied_positions_y,'ko',markersize = 2)
# plt.plot(tunnel_x, tunnel_y, 'ro', markersize = 1)
# plt.legend(['MPC solution','solution trajectory','end goal',' global path ', 'Obstacles', 'Feasible Bubbles'], loc = "best")
# plt.title('MPC Solution')
# plt.xlabel('x [m]')
# plt.ylabel('y [m]')
# plt.xlim([-0.5,12])
# plt.ylim([-0.2,10.2])
# plt.savefig('MPC solution', dpi=300)


# plt.figure(dpi=300)
# plt.plot(x_hist[0:i,0],y_hist[0:i,0], 'bo', markersize = 5)
# plt.plot(x_hist[0:i,0],y_hist[0:i,0], 'b-', markersize = 5)
# plt.plot(8.8,9,'bo', markersize = 10)
# plt.plot(global_path_x, global_path_y, 'g--')
# plt.plot(occupied_positions_x,occupied_positions_y,'ko',markersize = 2)
# plt.plot(tunnel_x, tunnel_y, 'ro', markersize = 1)
# plt.legend(['MPC solution','solution trajectory','end goal',' global path ', 'Obstacles', 'Feasible Bubbles'], loc = "best")
# plt.title('MPC Solution')
# plt.xlabel('x [m]')
# plt.ylabel('y [m]')
# plt.xlim([-0.5,12])
# plt.ylim([-0.2,10.2])
# plt.savefig('MPC solution controls', dpi=300)



# print("MPC solution time: ", time)






