function A_bl = Base4(T,A)

% T = Time;
% A = YNS_fil;

pad = 500; %pts
dt = mean(diff(T));
npts1 = length(T);
npts2 = npts1 + pad;
n = 1:npts2;

Tpad = dt*n';
Apad = [A;zeros(pad,1)];

Vpad=cumtrapz(Tpad,Apad);
Dpad=cumtrapz(Tpad,Vpad);


%% Apply polyfit only where V Taper is one (main vel pulse).
warning('off');

X = Tpad;
Y = Dpad;

ffun = fittype({'x.^2','x.^3','x.^4','x.^5','x.^6'});
beta = fit(X,Y,ffun);
fitted_model = feval(ffun,beta.a,beta.b,beta.c,beta.d,beta.e,X);

% params = 5;
% beta0=zeros(params,1);
% beta1=nlinfit(X,Y,@BaselinePoly,beta0); % first fun a fixed effects
% fitted_model = BaselinePoly(beta1,X);

d1 = diff(fitted_model(1:npts1))/dt; % derivative of fitted disp
d2 = diff(d1)/dt;         % second derivative of fitted disp
afit = [d2(1); d2; d2(end)];

A_bl = A-afit;

%%

%             V_bl = cumtrapz(T,A_bl);
%             D_bl = cumtrapz(T,V_bl);
%             scrsz = get(0,'ScreenSize');
%             figure('Position',[0.1*scrsz(3) 0.1*scrsz(4) 0.8*scrsz(3) 0.8*scrsz(4)])
%             subplot(3,1,1)
%             plot(T,A/100);hold on
%             plot(T,A_bl/100,'r:');
%             ylim([-1 1]);
%             xlabel('Time (sec)');
%             ylabel('Acc (m/sec2)');
%             legend('filtered acc','bl corrected acc');
%             subplot(3,1,2)
%             plot(T,Vpad(1:npts1),T,V_bl,'c');
%             xlabel('Time (sec)');
%             ylabel('Vel (cm/sec)');
%             legend('tapered vel','bl corrected vel');
%             subplot(3,1,3)
%             plot(X(1:npts1),Y(1:npts1),T,fitted_model(1:npts1),'r');hold on
%             plot(T,D_bl,'c');
%             ylim([-max(abs(Dpad)),max(abs(Dpad))]);grid on
%             xlabel('Time (sec)');
%             ylabel('Didp (cm)');
%             legend('disp data for fitting','curve fit','original disp data','bl corrected vel');
%             pause
%             close all

end