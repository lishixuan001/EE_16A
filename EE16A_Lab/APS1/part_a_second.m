function [result,result_b] = part_a_second()
  close all
  x = [0 1 2 3 4 5 6 7 8 9];
  y = [1 2 3 4 5 6 7 6 5 4];
  the_y = zeros(10,10);
  the_y(1,:) = y;
  for i = 2:10
    index = i - 1;
    the_y(i,:) = [y(i:end), y(1:index)];
  end
  result = the_y * y';
  figure(1);
  plot (x,result);
  y_of_first = [2 -2 2 -2 -2 -2 2 -2 2 2];
  figure(2);
  result_b = the_y * y_of_first';
  plot(x, result_b);
end
