FROM gitpod/workspace-full

# Install dependencies for Erlang build (Ubuntu 24.04)
RUN sudo apt-get update && sudo apt-get install -y \
    build-essential \
    autoconf \
    m4 \
    libncurses-dev \
    libssl-dev \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    libpng-dev \
    libssh-dev \
    unixodbc-dev \
    xsltproc \
    fop \
    libxml2-utils \
    openjdk-17-jdk \
    libwxgtk3.2-dev \
    git curl unzip

# Setup asdf
RUN git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.14.0
ENV PATH="/home/gitpod/.asdf/bin:/home/gitpod/.asdf/shims:$PATH"
RUN echo '. $HOME/.asdf/asdf.sh' >> ~/.bashrc

# Install Erlang & Elixir via asdf
RUN bash -c ". $HOME/.asdf/asdf.sh && \
    asdf plugin add erlang https://github.com/asdf-vm/asdf-erlang.git && \
    asdf plugin add elixir https://github.com/asdf-vm/asdf-elixir.git && \
    asdf install erlang 28.0 && \
    asdf global erlang 28.0 && \
    asdf install elixir 1.18.4 && \
    asdf global elixir 1.18.4"
