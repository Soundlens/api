# syntax=docker/dockerfile:1

FROM python:3.11.7-slim as base

# Set working directory
WORKDIR /var/www/html

# Never prompt the user for choices on installation/configuration of packages
ENV DEBIAN_FRONTEND=noninteractive
ENV TERM=linux
COPY flask/requirements.txt /var/www/html/requirements.txt

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        # Build dependencies
        gcc \
        libc-dev \
        # linux-headers-amd64 \
        git \
        supervisor \
        nginx \
        libmagic-dev \
        curl \
        libffi-dev \
        python3-dev \
        libpango1.0-dev \
        libbrotli-dev \
        # Audio processing dependencies
        libsndfile1 \
        ffmpeg \
        # AudioFlux dependencies
        cmake \
        build-essential \
        libfftw3-dev \
        # Fonts
        fonts-terminus \
        fonts-inconsolata \
        fonts-dejavu \
        fonts-noto \
        fonts-noto-cjk \
        fonts-font-awesome \
        fonts-noto-extra \
    && pip install -U pip \
    && pip install  weasyprint \
    # Install audioflux with its dependencies
    && AUDIOFLUX_USE_FFTW=1 pip install audioflux \
    && pip install -r requirements.txt \
    # Clean up
    && apt-get purge -y --auto-remove \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /usr/share/man /usr/share/doc

# Add a user for running the app
RUN useradd -G www-data -s /bin/sh -m mutable \
    && passwd -d mutable
# Development stage
FROM base as dev

# Install development tools and Node.js
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y \
        nano \
        vim \
        iputils-ping \
        bash \
        busybox-static \
        nodejs \
    && npm install -g npm@latest \
    && rm -rf /var/lib/apt/lists/*

# Copy supervisord configuration for development
COPY --chown=mutable common/supervisord.conf.dev /etc/supervisor/conf.d/supervisord.conf

ENTRYPOINT ["/bin/bash", "-c"]
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

# Production stage
FROM base as prod

# Install Node.js and npm properly for Debian-based system
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g pm2

# Copy supervisord, nginx, and uwsgi configuration files for production
COPY --chown=mutable common/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY --chown=mutable common/nginx.conf /etc/nginx/nginx.conf
COPY --chown=mutable common/wsgi.ini /etc/uwsgi/wsgi.ini
COPY --chown=mutable common/uwsgi_params /etc/nginx/uwsgi_params

# Copy application files
COPY --chown=mutable flask /var/www/html

# Build the frontend
WORKDIR /var/www/html/app/frontend
# Install dependencies and build



RUN npm install
RUN npm run build

# Create PM2 ecosystem file
COPY --chown=mutable common/ecosystem.config.js /var/www/html/app/frontend/ecosystem.config.js

WORKDIR /var/www/html

# Change ownership of runtime directory
RUN chown -R mutable /run


# install uwsgi via pip
RUN pip install uwsgi

# Set ownership
# WORKDIR /var/www/html
# RUN chown -R mutable /var/www/html/webapp

CMD [ "/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf"]
ENTRYPOINT [ "/bin/sh", "-c" ]
HEALTHCHECK --interval=15m --timeout=5s --retries=3 \
    CMD ["/usr/bin/curl", "--fail", "http://localhost:8080/health"]