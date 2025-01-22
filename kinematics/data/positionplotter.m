clear all
close all


positions = sortrows(dlmread ('positions.csv',',',2,0), 3);

slice_size = 5; # mm
curr_slice = 0
curr_pos_index = 1
radiuses = []
while true
  start_pos_index = curr_pos_index;
  max_radius = 0.0;
  for i  = start_pos_index:rows(positions)
    if positions(i, 3) > (curr_slice+1) * slice_size
      break;
    endif
    radius = positions(i, 1)^2 + positions(i, 2)^2;
    if radius > max_radius
      max_radius = radius;
    endif
    curr_pos_index = curr_pos_index+1;
    
  endfor
  if curr_pos_index >= rows(positions)
    break;
  endif
  curr_slice = curr_slice+1;
  radiuses = [radiuses;sqrt(max_radius)]
endwhile

figure(1)
mesh(positions(:, 1), positions(:, 2), positions(:, 3), 'or')
title("positions effecteur mm")

radiuses
height = positions(end, 3) - positions(1, 3)
maxheight = positions(end, 3)