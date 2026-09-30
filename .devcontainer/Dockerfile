FROM mcr.microsoft.com/devcontainers/base:bookworm

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN test "$(dpkg --print-architecture)" = amd64 \
    && apt-get update && apt-get install -y --no-install-recommends \
       curl unzip python3 ca-certificates libgtk-3-0 libnss3 libasound2 \
       libgbm1 libxss1 libxtst6 libx11-xcb1 libgl1-mesa-dri libglu1-mesa \
       libxkbcommon0 libnotify4 libsecret-1-0 libsdl2-2.0-0 wmctrl xdotool \
    && apt-get clean

# Match the repository's JetBrains Java 21 daemon criteria.
ARG JBR_ARCHIVE=jbrsdk-21.0.11-linux-x64-b1163.116.tar.gz
RUN mkdir -p /opt/ftc/jdk /opt/android-sdk/cmdline-tools \
    && curl -fL --retry 3 "https://cache-redirector.jetbrains.com/intellij-jbr/${JBR_ARCHIVE}" -o /tmp/jbr.tar.gz \
    && curl -fL --retry 3 "https://cache-redirector.jetbrains.com/intellij-jbr/${JBR_ARCHIVE}.checksum" -o /tmp/jbr.sha512 \
    && printf '%s  /tmp/jbr.tar.gz\n' "$(awk '{print $1}' /tmp/jbr.sha512)" | sha512sum -c - \
    && tar -xzf /tmp/jbr.tar.gz --strip-components=1 -C /opt/ftc/jdk \
    && rm /tmp/jbr.tar.gz /tmp/jbr.sha512

ENV JAVA_HOME=/opt/ftc/jdk ANDROID_HOME=/opt/android-sdk ANDROID_SDK_ROOT=/opt/android-sdk
ENV PATH="/opt/ftc/jdk/bin:/opt/android-sdk/cmdline-tools/latest/bin:${PATH}"
RUN curl -fL --retry 3 https://dl.google.com/android/repository/commandlinetools-linux-15859902_latest.zip -o /tmp/android-tools.zip \
    && echo '4e4c464f145a7512b57d088ac6c278c03c9eea610886b35a5e0804e74eedf583  /tmp/android-tools.zip' | sha256sum -c - \
    && unzip -q /tmp/android-tools.zip -d /opt/android-sdk/cmdline-tools \
    && mv /opt/android-sdk/cmdline-tools/cmdline-tools /opt/android-sdk/cmdline-tools/latest \
    && rm /tmp/android-tools.zip \
    && chown -R vscode:vscode /opt/android-sdk

ARG ASCOPE_VERSION=26.0.2
RUN curl -fL --retry 3 "https://github.com/Mechanical-Advantage/AdvantageScope/releases/download/v${ASCOPE_VERSION}/advantagescope-linux-x64-v${ASCOPE_VERSION}.AppImage" -o /tmp/ascope.AppImage \
    && echo 'd5ec30f285f9a241fca97d384887070d36c8a70bd8ee17fdb92c933663ee3396  /tmp/ascope.AppImage' | sha256sum -c - \
    && chmod +x /tmp/ascope.AppImage \
    && cd /opt/ftc && /tmp/ascope.AppImage --appimage-extract >/dev/null \
    && chmod -R a+rX /opt/ftc/squashfs-root \
    && chmod a+x /opt/ftc/squashfs-root/AppRun \
    && runuser -u vscode -- test -x /opt/ftc/squashfs-root/AppRun \
    && rm /tmp/ascope.AppImage

COPY cloud/advantagescope.sh /opt/ftc/Programs/advantagescope/AdvantageScope.exe
RUN chmod +x /opt/ftc/Programs/advantagescope/AdvantageScope.exe
ENV LOCALAPPDATA=/opt/ftc LIBGL_ALWAYS_SOFTWARE=1
