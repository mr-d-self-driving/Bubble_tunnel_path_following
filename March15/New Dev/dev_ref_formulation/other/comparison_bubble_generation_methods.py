<<<<<<< HEAD

from Bubble_tunnel_generation_v2 import generate_bubbles_v2
from Grid_generation import create_obstacles, create_global_path
from Bubble_tunnel_generation_Mat import defineDiscreteBubbles
import time
import matplotlib.pyplot as plt
import numpy as np
from Bubble_tunnel_generation_v2 import create_tunnel

#----------------------------------------------------------------------------#
#                         Generate Grid and Obstacles                        #
#----------------------------------------------------------------------------#

end_goal_x      =   9     # position of initial and end point
end_goal_y      =   9
initial_pos_x   =   0
initial_pos_y   =   0
xlim_min        =   -0.2  # xlim and ylim of plots
xlim_max        =   10
ylim_min        =   -0.2
ylim_max        =   15
n               =   10    # size of square grid


''' 
possible combinations of the two options below: 1/1 2/1

option 1/1 works 

option 2/1 doesnt work = its is a very hard situiation 
                       = the bubbles stop generating (side effect of no wall crossing technique)

''' 
obstacles_option = 1 
path_option = 1


n = 300




"""
# n = 40 points = 200

time needed for generating of bubbles / new method v2 / in seconds:  0.0319
time needed for generating of bubbles / old method / in seconds:  0.182

# n = 50  points = 250

time needed for generating of bubbles / new method v2 / in seconds:  0.0369
time needed for generating of bubbles / old method / in seconds:  0.222


# for n = 100 ==== 500 points of obstacles

time needed for generating of bubbles / new method v2 / in seconds:  0.0628
time needed for generating of bubbles / old method / in seconds:  0.455


# for n = 200 ==== 1000 points of obstacles
time needed for generating of bubbles / new method v2 / in seconds:  0.123
time needed for generating of bubbles / old method / in seconds:  0.894


# for n = 250 ==== 1250 points of obstacles
time needed for generating of bubbles / new method v2 / in seconds:  0.167
time needed for generating of bubbles / old method / in seconds:  1.144

# for n = 300 ==== 1500 points of obstacles
time needed for generating of bubbles / new method v2 / in seconds:  0.2144
time needed for generating of bubbles / old method / in seconds:  1.275

# for n = 350 ==== 1750
time needed for generating of bubbles / new method v2 / in seconds:  0.240
time needed for generating of bubbles / old method / in seconds:  1.55
# for n = 400 ==== 2000
time needed for generating of bubbles / new method v2 / in seconds:  0.278
time needed for generating of bubbles / old method / in seconds:  1.876


"""

time_old = 1000*np.array([0.182, 0.222, 0.455, 0.894, 1.144, 1.275, 1.55, 1.876])
time_new = 1000*np.array([0.0319, 0.0369, 0.0628, 0.123, 0.167, 0.214, 0.240, 0.278])
points   = np.array([200, 250, 500, 1000, 1250, 1500, 1750, 2000])

mo, bo = np.polyfit(points, time_old, 1)
mn, bn = np.polyfit(points, time_new, 1)

yo = mo*points + bo
yn = mn*points + bn

plt.figure()
plt.plot(points, time_old, 'o')
plt.plot(points, time_new, 'o')
plt.plot(points, yo)
plt.plot(points, yn)
plt.legend(['execution time of old method', 'execution time of new method', 't = (0.91*points - 8.25) ms', 't = (0.14*points - 2.06) ms'])
plt.xlabel('number of obstacle points')
plt.ylabel('time in ms')
plt.title('execution time of old and new Bubble generation methods on Python')
plt.savefig('time exc comparison', dpi=300)











occupied_positions_x = np.linspace(0,9,n)
occupied_positions_y = 10*np.ones(n)

#line at x = 3
occupied_positions_x = np.concatenate((occupied_positions_x, 3*np.ones(n)))
occupied_positions_y = np.concatenate((occupied_positions_y,   np.linspace(0,8,n)))

#line at x = 7
occupied_positions_x = np.concatenate((occupied_positions_x, 7*np.ones(n)))
occupied_positions_y = np.concatenate((occupied_positions_y,   np.linspace(0,8,n)))

#line at y = 0
occupied_positions_x = np.concatenate((occupied_positions_x,   np.linspace(3,7,n)))
occupied_positions_y = np.concatenate((occupied_positions_y, 0*np.ones(n)))

#line at y = 8
occupied_positions_x = np.concatenate((occupied_positions_x,   np.linspace(7,9,n)))
occupied_positions_y = np.concatenate((occupied_positions_y, 8*np.ones(n)))
        


Bspline_obj, global_path = create_global_path(path_option)

#----------------------------------------------------------------------------#
#                           Creating the Bubbles                             #
#----------------------------------------------------------------------------#

start_time = time.time()

# # new method
# f_x, f_y,sx,sy,mx, my, r, smx, smy, sr \
#     = generate_bubbles(global_path,Bspline_obj,occupied_positions_x,occupied_positions_y)

end_time_1 = time.time()

# new method v2
shifted_midpoints_x, shifted_midpoints_y, shifted_radii\
= generate_bubbles_v2(global_path[0],global_path[1],occupied_positions_x,occupied_positions_y)

end_time_2 = time.time()

#old method
occupied_positions = []    
for i in range(0, len(occupied_positions_x)):    
    occupied_positions.append([occupied_positions_x[i], occupied_positions_y[i]])
    
feasiblebubbles_x_mat, feasiblebubbles_y_mat, radii_mat, midpoints_x_mat, midpoints_y_mat \
    = defineDiscreteBubbles(Bspline_obj,occupied_positions_x,occupied_positions_y)  
 
end_time_3 = time.time()



#----------------------------------------------------------------------------#
#                         Comparison - time                                  #
#----------------------------------------------------------------------------#


print("time needed for generating of bubbles / new method / in seconds: "    , end_time_1 - start_time)
print("time needed for generating of bubbles / new method v2 / in seconds: " , end_time_2 - end_time_1)
print("time needed for generating of bubbles / old method / in seconds: "    , end_time_3 - end_time_2)



#----------------------------------------------------------------------------#
#                    Create feasible bubble points                           #
#----------------------------------------------------------------------------#


npoints =  500  #numbr of points of every circle
ts      =  np.linspace(0, 2*np.pi, npoints) #for creating circles points
    
shifted_feasiblebubbles_x = []
shifted_feasiblebubbles_y = []
for i in range (0, len(shifted_midpoints_x)):
        shifted_feasiblebubbles_x.append(shifted_midpoints_x[i] + shifted_radii[i]*np.cos(ts))
        shifted_feasiblebubbles_y.append(shifted_midpoints_y[i] + shifted_radii[i]*np.sin(ts))


tunnel_x, tunnel_y = create_tunnel(shifted_midpoints_x,shifted_midpoints_y,shifted_radii)
tunnel_x_mat, tunnel_y_mat = create_tunnel(midpoints_x_mat,midpoints_y_mat,radii_mat)

#----------------------------------------------------------------------------#
#                         Comparison - Plots                                 #
#----------------------------------------------------------------------------#

         

# plt.figure()
# plt.plot(global_path[0], global_path[1], 'b-')
# plt.plot(shifted_midpoints_x, shifted_midpoints_y, 'rx')
# plt.plot(occupied_positions_x, occupied_positions_y, 'o', markersize= 2)
# plt.plot(shifted_feasiblebubbles_x,shifted_feasiblebubbles_y,'gx',markersize= 0.5)
# plt.legend(['Global Reference Trajectory','Midpoints of the bubbles', 'Occupied Positions', 'feasible bubbles'])
# plt.title('Results of new method with shifting bubbles')
# plt.xlabel('x [m]')
# plt.ylabel('y [m]')
# plt.xlim([xlim_min,xlim_max])
# plt.ylim([ylim_min,ylim_max])
# plt.savefig('Results of new method with shifting bubbles', dpi=300)


# plt.figure()
# plt.plot(global_path[0], global_path[1], 'b-')
# plt.plot(midpoints_x_mat, midpoints_y_mat, 'rx')
# plt.plot(occupied_positions_x, occupied_positions_y, 'o', markersize= 2)
# plt.legend(['Global Reference Trajectory','Midpoints of the bubbles', 'Occupied Positions'], loc = 'best')
# plt.title('Results of old method')
# plt.xlabel('x [m]')
# plt.ylabel('y [m]')
# plt.xlim([xlim_min,xlim_max])
# plt.ylim([ylim_min,ylim_max])
# plt.savefig('Results of old method midpoints', dpi=300)

# plt.figure()
# plt.plot(global_path[0], global_path[1], 'b-')
# plt.plot(shifted_midpoints_x, shifted_midpoints_y, 'rx')
# plt.plot(occupied_positions_x, occupied_positions_y, 'o', markersize= 2)
# plt.legend(['Global Reference Trajectory','Midpoints of the bubbles', 'Occupied Positions'], loc = 'best')
# plt.title('Results of new method')
# plt.xlabel('x [m]')
# plt.ylabel('y [m]')
# plt.xlim([xlim_min,xlim_max])
# plt.ylim([ylim_min,ylim_max])
# plt.savefig('Results of mew method midpoints', dpi=300)

# plt.figure()
# plt.plot(global_path[0], global_path[1], 'b-')
# plt.plot(midpoints_x_mat, midpoints_y_mat, 'rx')
# plt.plot(occupied_positions_x, occupied_positions_y, 'o', markersize= 2)
# plt.plot(feasiblebubbles_x_mat,feasiblebubbles_y_mat,'yx',markersize= 0.5)
# plt.legend(['Global Reference Trajectory','Midpoints of the bubbles', 'Occupied Positions','feasible bubbles'])
# plt.title('Results of old method')
# plt.xlabel('x [m]')
# plt.ylabel('y [m]')
# plt.xlim([xlim_min,xlim_max])
# plt.ylim([ylim_min,ylim_max])
# plt.savefig('Results of old method 2', dpi=300)


# plt.figure()
# plt.plot(shifted_radii, 'ro')
# plt.plot(radii_mat, 'bo')
# plt.legend(['Bubbles radii improved method','Bubbles radii old method'])
# plt.title('Comparison radii values')
# plt.ylabel('radius [m]')
# plt.savefig('comparison radii', dpi=300)

# plt.figure()
# plt.plot(global_path[0], global_path[1], 'b-')
# plt.plot(shifted_midpoints_x, shifted_midpoints_y, 'gx')
# plt.plot(occupied_positions_x, occupied_positions_y, 'o', markersize= 2)
# plt.plot(tunnel_x,tunnel_y,'y.',markersize= 1)
# plt.legend(['Global Reference Trajectory','Midpoints of the bubbles', 'Occupied Positions','Resulting feasible tunnel'])
# plt.title('Results of new method')
# plt.xlabel('x [m]')
# plt.ylabel('y [m]')
# plt.xlim([xlim_min,xlim_max])
# plt.ylim([ylim_min,ylim_max])
# plt.savefig('Tunnel comparison 1', dpi=300)

# plt.figure()
# plt.plot(global_path[0], global_path[1], 'b-')
# plt.plot(midpoints_x_mat, midpoints_y_mat, 'gx')
# plt.plot(occupied_positions_x, occupied_positions_y, 'o', markersize= 2)
# plt.plot(tunnel_x_mat,tunnel_y_mat,'r.',markersize= 1)
# plt.legend(['Global Reference Trajectory','Midpoints of the bubbles', 'Occupied Positions','Resulting feasible tunnel'])
# plt.title('Results of old method')
# plt.xlabel('x [m]')
# plt.ylabel('y [m]')
# plt.xlim([xlim_min,xlim_max])
# plt.ylim([ylim_min,ylim_max])
# plt.savefig('Tunnel comparison 2', dpi=300)




















=======
# from Bubble_tunnel_generation import generate_bubbles
from Bubble_tunnel_generation_v2 import generate_bubbles_v2
from Grid_generation import create_obstacles, create_global_path
from Bubble_tunnel_generation_Mat import defineDiscreteBubbles
import time
import matplotlib.pyplot as plt
import numpy as np

#----------------------------------------------------------------------------#
#                         Generate Grid and Obstacles                        #
#----------------------------------------------------------------------------#

end_goal_x      =   9     # position of initial and end point
end_goal_y      =   9
initial_pos_x   =   0
initial_pos_y   =   0
xlim_min        =   -0.5  # xlim and ylim of plots
xlim_max        =   10.5
ylim_min        =   -3
ylim_max        =   14
n               =   10    # size of square grid


''' 
possible combinations of the two options below: 1/1 2/1

option 1/1 works 

option 2/1 doesnt work = its is a very hard situiation 
                       = the bubbles stop generating (side effect of no wall crossing technique)

''' 
obstacles_option = 1 
path_option = 1

occupied_positions_x, occupied_positions_y = create_obstacles(obstacles_option)
Bspline_obj, global_path = create_global_path(path_option)

#----------------------------------------------------------------------------#
#                           Creating the Bubbles                             #
#----------------------------------------------------------------------------#

start_time = time.time()

# # new method
# f_x, f_y,sx,sy,mx, my, r, smx, smy, sr \
#     = generate_bubbles(global_path,Bspline_obj,occupied_positions_x,occupied_positions_y)

end_time_1 = time.time()

# new method v2
shifted_midpoints_x, shifted_midpoints_y, shifted_radii\
= generate_bubbles_v2(global_path[0],global_path[1],occupied_positions_x,occupied_positions_y)

end_time_2 = time.time()

#old method
occupied_positions = []    
for i in range(0, len(occupied_positions_x)):    
    occupied_positions.append([occupied_positions_x[i], occupied_positions_y[i]])
    
feasiblebubbles_x_mat, feasiblebubbles_y_mat, radii_mat, midpoints_x_mat, midpoints_y_mat \
    = defineDiscreteBubbles(Bspline_obj,occupied_positions_x,occupied_positions_y)  
 
end_time_3 = time.time()



#----------------------------------------------------------------------------#
#                         Comparison - time                                  #
#----------------------------------------------------------------------------#


print("time needed for generating of bubbles / new method / in seconds: "    , end_time_1 - start_time)
print("time needed for generating of bubbles / new method v2 / in seconds: " , end_time_2 - end_time_1)
print("time needed for generating of bubbles / old method / in seconds: "    , end_time_3 - end_time_2)



#----------------------------------------------------------------------------#
#                    Create feasible bubble points                           #
#----------------------------------------------------------------------------#


npoints =  500  #numbr of points of every circle
ts      =  np.linspace(0, 2*np.pi, npoints) #for creating circles points
    
shifted_feasiblebubbles_x = []
shifted_feasiblebubbles_y = []
for i in range (0, len(shifted_midpoints_x)):
        shifted_feasiblebubbles_x.append(shifted_midpoints_x[i] + shifted_radii[i]*np.cos(ts))
        shifted_feasiblebubbles_y.append(shifted_midpoints_y[i] + shifted_radii[i]*np.sin(ts))





#----------------------------------------------------------------------------#
#                         Comparison - Plots                                 #
#----------------------------------------------------------------------------#

         

plt.figure()
plt.plot(global_path[0], global_path[1], 'b-')
plt.plot(shifted_midpoints_x, shifted_midpoints_y, 'rx')
plt.plot(occupied_positions_x, occupied_positions_y, 'o', markersize= 2)
plt.plot(shifted_feasiblebubbles_x,shifted_feasiblebubbles_y,'gx',markersize= 0.5)
plt.legend(['Global Reference Trajectory','Midpoints of the bubbles', 'Occupied Positions'])
plt.title('Results of new method with shifting bubbles')
plt.xlabel('x [m]')
plt.ylabel('y [m]')
plt.xlim([xlim_min,xlim_max])
plt.ylim([ylim_min,ylim_max])



# plt.figure()
# plt.plot(global_path[0], global_path[1], 'b-')
# plt.plot(midpoints_x_mat, midpoints_y_mat, 'rx')
# plt.plot(occupied_positions_x, occupied_positions_y, 'o', markersize= 2)
# plt.legend(['Global Reference Trajectory','Midpoints of the bubbles', 'Occupied Positions'])
# plt.title('Results of old method')
# plt.xlabel('x [m]')
# plt.ylabel('y [m]')
# plt.xlim([xlim_min,xlim_max])
# plt.ylim([ylim_min,ylim_max])

# plt.figure()
# plt.plot(global_path[0], global_path[1], 'b-')
# plt.plot(midpoints_x_mat, midpoints_y_mat, 'rx')
# plt.plot(occupied_positions_x, occupied_positions_y, 'o', markersize= 2)
# plt.plot(feasiblebubbles_x_mat,feasiblebubbles_y_mat,'yx',markersize= 0.5)
# plt.legend(['Global Reference Trajectory','Midpoints of the bubbles', 'Occupied Positions'])
# plt.title('Results of old method')
# plt.xlabel('x [m]')
# plt.ylabel('y [m]')
# plt.xlim([xlim_min,xlim_max])
# plt.ylim([ylim_min,ylim_max])






















>>>>>>> ec2c2a2079a30fafd3c06d2aab4e6b92537a013a
