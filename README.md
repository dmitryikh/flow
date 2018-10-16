deploy:

```bash
cd flow
python setup.py install
python setup.py test

cd ../rss_app
python setup.py install
python setup.py test

# check that installed ok
rss_app -h

# run app
rss_app
```
