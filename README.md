# HackaTUM24
Our solution for the Hubert Bourdas' challenge at HackaTUM24

## API Keys Instructions
Fill in your keys in [.env-example](./.env-example) and rename it to `.env`

## Prototyping installation instructions

```bash
conda create -n hackatum python=3.11
conda activate hackatum
pip install -r requirements.txt
```

## Collecting News Data
```bash
python news_collector/news_aggregator.py
```

## Scoring and Filtering Articles
```bash
python feed_filtering/filter_feed.py
``` 

## KNN Clustering
Run [knn_clustering/knn_clustering.py](./knn_clustering/knn_clustering.py) to cluster the articles.


## Local Development

### Backend
In one terminal:
```bash
python api.py
```

### Frontend
Note that Node.js version "^18.18.0 || ^19.8.0 || >= 20.0.0" is required.
In another terminal:
```bash
cd frontend
npm install
npm run dev
```


