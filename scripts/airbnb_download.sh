# Run from user/repo_name
url="https://disk.yandex.ru/d/nVlQMdP7uSxxNA"

wget "$(yadisk-direct $url)" -O ./data/airbnb_24.zip

unzip data/airbnb_24.zip -d data/airbnb_24

# Move from inner folder to ./data
cp data/airbnb_24/public/airbnb_24.csv data/airbnb_24.csv
rm -rf data/airbnb_24
rm data/airbnb_24.zip