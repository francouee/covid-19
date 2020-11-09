#!/bin/sh

conda activate covid19
python /Users/Francois/Documents/Programmation/Python/Divers/Coronavirus/src/generate_plot_html.py
current_date=${date +"%d/%m/%y"}
git add .
git commit -m "updated data ${current_date}"
git push
