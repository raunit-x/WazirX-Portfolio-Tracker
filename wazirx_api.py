from collections import namedtuple


WazirX = namedtuple('WazirXApiDetails', 'BASE_API_ENDPOINT VERSION')

wazirx_api_details = WazirX('https://api.wazirx.com', 'api/v2')
