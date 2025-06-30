git clone https://github.com/OpenTalker/SadTalker.git
cd SadTalker 
conda create -n sadtalker python=3.8
conda activate sadtalker
conda install ffmpeg
pip install -r requirements.txt
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip show torch | grep Location
pip uninstall basicsr gfpgan -y
pip install git+https://github.com/xinntao/BasicSR.git
pip install git+https://github.com/TencentARC/GFPGAN.git
pip install opencv-python facexlib
python inference.py --driven_audio sample.wav --source_image sample.jpeg --enhancer gfpgan

# Create symbolic link to make SadTalker accessible from the parent project
cd ..
ln -s SadTalker/src ./lip-sync-app/src
echo "Created symbolic link: lip-sync-app/src -> SadTalker/src"

# Create environment file for local development
cd lip-sync-app
echo "export SADTALKER_PATH=\"$(pwd)/../SadTalker\"" > .env.local
echo "Created .env.local with SADTALKER_PATH"
echo ""
echo "SadTalker setup complete!"
echo "For local development, run: source .env.local"
echo "Then you can start your lip-sync-app locally."
