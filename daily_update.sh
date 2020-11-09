#!/bin/sh

conda init zsh
conda activate covid19
cd /Users/Francois/Documents/Programmation/Python/Divers/Coronavirus/src
python generate_plot_html.py
cd ..
current_date=$(date +"%d/%m/%y")
git add .
git commit -m "updated data $current_date"
git push
