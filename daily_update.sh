#!/bin/sh
#00 17 * * * /Users/Francois/Documents/Programmation/Python/Divers/Coronavirus/.daily_update.sh

source $HOME/.zshrc
conda activate covid19
cd /Users/Francois/Documents/Programmation/Python/Divers/Coronavirus/src
python generate_plot_html.py
cd ..
current_date=$(date +"%d/%m/%y")
git add .
git commit -m "updated data $current_date"
git push
