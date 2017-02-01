
from veda_worker import VedaWorker

VW = VedaWorker()

VW = VedaWorker(
    veda_id='XXXXXXXXT114-V013800',
    encode_profile = 'hls',
    jobid = 'xxxxx'
)

VW.run()
