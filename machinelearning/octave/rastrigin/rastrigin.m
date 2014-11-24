
close all;

function retval = rastriginsfcn(x)
  x1 = x(:, 1);
  x2 = x(:, 2);
  retval = 20 + (x1 .** 2) + (x2 .** 2) - 10 .* (cos (2 .* pi .* x1) +
                                                 cos (2 .* pi .* x2));
endfunction

%x = linspace(-5.12, 5.12, 100);
x = linspace(-6, 6, 300);
X = repmat(x, 2, 1)';

% 2D plot
figure;
plot(x, rastriginsfcn(X), '-b', 'LineWidth', 1);
xlabel('x'); ylabel('y');
title("Rastrigin Function");

y = zeros(length(x), length(x));
for i = 1:length(x)
  for j = 1:length(x) 
	  y(i,j) = rastriginsfcn([x(i), x(j)]);
  end
end

% 3D surface plot
figure;
surfc(x, x, y);
%shading interp;
grid off;
%title("Rastrigin Function");
%contour(x, x, y, linspace(-5.12, 5.12, 1.0));

