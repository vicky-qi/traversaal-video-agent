# Traversaal Video Agent in one container: the web app plus the whole video pipeline.
#   docker build -t traversaal-video-agent .
#   docker run -p 7860:7860 -e ANTHROPIC_API_KEY=sk-ant-... -e APP_ACCESS_CODE=pick-a-code traversaal-video-agent
# Then open http://localhost:7860. See app/README.md for hosting it online.
FROM condaforge/miniforge3:25.11.0-1

# Libraries Chrome Headless Shell needs to render scenes, plus fonts.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libasound2t64 libatk-bridge2.0-0t64 libatk1.0-0t64 libcairo2 libcups2t64 libdbus-1-3 libdrm2 \
        libgbm1 libglib2.0-0t64 libnspr4 libnss3 libpango-1.0-0 libxcomposite1 libxdamage1 libxfixes3 \
        libxkbcommon0 libxrandr2 libxshmfence1 libx11-xcb1 fonts-liberation fonts-noto-color-emoji unzip \
    && rm -rf /var/lib/apt/lists/*

# The team's own `video` environment (environment.yml), plus the app's packages.
COPY environment.yml /tmp/environment.yml
RUN conda env create -f /tmp/environment.yml && conda clean -afy
COPY app/requirements.txt /tmp/app-requirements.txt
RUN conda run -n video pip install --no-cache-dir -r /tmp/app-requirements.txt

# Hosts such as Hugging Face Spaces run the container as user 1000.
RUN (userdel -r ubuntu 2>/dev/null || true) && useradd -m -u 1000 user
USER user
ENV HOME=/home/user PORT=7860
WORKDIR /home/user/app
COPY --chown=user . .

# Fetch the render browser and the voice model now, so the first video does not wait for them.
RUN render/env.sh npx --yes hyperframes@0.8.140 telemetry disable \
 && render/env.sh npx --yes hyperframes@0.8.140 browser ensure \
 && render/env.sh npx --yes hyperframes@0.8.140 tts "Ready." -o /tmp/warmup.wav \
 && rm /tmp/warmup.wav

EXPOSE 7860
CMD ["sh", "-c", "exec render/env.sh python -m uvicorn app.server:app --host 0.0.0.0 --port ${PORT}"]
