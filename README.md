# routeview_loop
Script to check if certain prefix exists in the Internet

# Install
```
pip install -r requirements.txt
```
# RUN
```
○ → python routeview.py  -h
usage: routeview.py [-h] -r PREFIX -a ASN -s SLEEP -t TRANSIT

optional arguments:
  -h, --help            show this help message and exit
  -r PREFIX, --prefix PREFIX
                        Check ipv4 route in routing table
  -a ASN, --asn ASN     ASN that we want to check
  -s SLEEP, --sleep SLEEP
                        Sleep for how long
  -t TRANSIT, --transit TRANSIT
                        A list of transit asns eg:
                        '174,1299,3356,5511,3257,2914,7922,1221,4637'

○ → python routeview.py  -r 1.1.1.0/24 -a 13335 -s 30 -t '174,1299,3356,5511,3257,2914,7922,1221,4637'
[14:16:16] connecting to routeview                                                                                                                                                                    routeview.py:64
[14:16:17] sending username                                                                                                                                                                           routeview.py:67
           connected to routeview                                                                                                                                                                     routeview.py:70
[14:16:19] transit path:9 unique transit:{'1221', '2914', '3257', '3356'}                                                                                                                             routeview.py:57
           peering path:19                                                                                                                                                                            routeview.py:60

```
