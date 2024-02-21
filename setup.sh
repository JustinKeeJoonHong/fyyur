#!/bin/bash
source /Users/hong-gijun/opt/anaconda3/etc/profile.d/conda.sh
conda deactivate

deactivate 2>/dev/null || true

source /Users/hong-gijun/fyyurenv/bin/activate
cd /Users/hong-gijun/Desktop/fyyur
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1
flask run
# conda deactivate
# flask run