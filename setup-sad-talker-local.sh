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