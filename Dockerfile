FROM ros:jazzy

# Install essentials + Gazebo Harmonic + RViz2
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-venv \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-argcomplete \
    ros-jazzy-ros-gz \
    ros-jazzy-ros-gz-sim \
    ros-jazzy-ros-gz-bridge \
    ros-jazzy-ros-gz-interfaces \
    ros-jazzy-gz-sensors-vendor \
    ros-jazzy-gz-rendering-vendor \
    ros-jazzy-rviz2 \
    ros-jazzy-rqt \
    ros-jazzy-rqt-common-plugins \
    ros-jazzy-robot-state-publisher \
    ros-jazzy-tf2-ros \
    ros-jazzy-tf2-tools \
    ros-jazzy-topic-tools \
    libgl1 \
    libglx-mesa0 \
    libgles2 \
    libegl1 \
    libegl-mesa0 \
    libglvnd0 \
    libglvnd-dev \
    mesa-utils \
    git vim nano wget curl tmux htop \
    && rm -rf /var/lib/apt/lists/*

# Initialize rosdep
RUN rosdep init || true && rosdep update

# Create workspace and venv
RUN mkdir -p /ros2_ws/src
RUN python3 -m venv /ros2_ws/.venv --system-site-packages

# Auto source on shell start
RUN echo "source /opt/ros/jazzy/setup.bash" >> /root/.bashrc
RUN echo "source /ros2_ws/install/setup.bash 2>/dev/null || true" >> /root/.bashrc
RUN echo "source /ros2_ws/.venv/bin/activate" >> /root/.bashrc
RUN echo "export ROS_DOMAIN_ID=55" >> /root/.bashrc
RUN echo "export RCUTILS_COLORIZED_OUTPUT=1" >> /root/.bashrc
RUN echo "export GZ_SIM_SYSTEM_PLUGIN_PATH=/opt/ros/jazzy/opt/gz_sim_vendor/lib/gz-sim-8/plugins/" >> /root/.bashrc
RUN echo "export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:/opt/ros/jazzy/opt/gz_sensors_vendor/lib/" >> /root/.bashrc
RUN echo "export NVIDIA_VISIBLE_DEVICES=all" >> /root/.bashrc
RUN echo "export NVIDIA_DRIVER_CAPABILITIES=all" >> /root/.bashrc
RUN echo "export __NV_PRIME_RENDER_OFFLOAD=1" >> /root/.bashrc
RUN echo "export __GLX_VENDOR_LIBRARY_NAME=nvidia" >> /root/.bashrc
RUN echo "export EGL_PLATFORM=device" >> /root/.bashrc
RUN echo 'export PS1="(.venv) \[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]# "' >> /root/.bashrc

# Terminal colors
ENV TERM=xterm-256color
ENV FORCE_COLOR=1

# NVIDIA env vars at image level
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=all
ENV __NV_PRIME_RENDER_OFFLOAD=1
ENV __GLX_VENDOR_LIBRARY_NAME=nvidia
ENV EGL_PLATFORM=device
ENV ROS_DOMAIN_ID=55

WORKDIR /ros2_ws
CMD ["bash"]
