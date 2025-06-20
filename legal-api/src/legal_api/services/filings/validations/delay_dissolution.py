# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Validation for Delay Dissolution filing."""
from enum import Enum
from http import HTTPStatus
from typing import Dict, Final, Optional

import pycountry
from flask_babel import _

from legal_api.errors import Error
from legal_api.models import Address, Business, PartyRole

from .common_validations import validate_court_order, validate_pdf
from ...utils import get_str, get_bool, get_int, get_date # noqa: I003; needed as the linter gets confused from the babel override above.
from datetime import datetime
from dateutil.relativedelta import relativedelta

def validate(business: Business, delayDissolution: Dict) -> Optional[Error]:
    """Validate the dissolution filing"""
    if not business or not delayDissolution:
        return Error(HTTPStatus.BAD_REQUEST, [{'error': _('A valid business and filing are required.')}])
    msg = []

    err = validate_business_state(business)
    if err:
        msg.extend(err)

    err = validate_date(delayDissolution)
    if err:
        msg.extend(err)

    err = validate_delays(delayDissolution)
    if err:
        msg.extend(err)

    if msg:
        return Error(HTTPStatus.BAD_REQUEST, msg)
    return None

def validate_business_state(business) -> Optional[list]:
    """Validate busness is not frozen"""
    msg = []
    current_state = business.admin_freeze or False

    if current_state == True:
        msg.append({'error': _('Dissolution cannot be delayed on frozen businesses.'), 'path': '/business/adminFreeze'})
        return msg

    return None


def validate_delays(filing_json) -> Optional[list]:
    """Validate number of delays"""
    msg = []
    
    dissolution_delay_path = '/filing/delayDissolution/numberOfDelays'
    dissolution_delay_number = get_int(filing_json, dissolution_delay_path)

    #may need to hit database to check numberOfDelays

    if dissolution_delay_number >= 2:
        msg.append({'error': _('Dissolution may only be delayed twice'), 'path': dissolution_delay_path})
        return msg

    return None


def validate_date(filing_json) -> Optional[list]:
    """Validate date"""
    msg = []
    dissolution_date_path = '/filing/delayDissolution/dissolutionDate'
    dissolution_date = get_date(filing_json, dissolution_date_path)
    now = datetime.now().date()
    two_years = now + relativedelta(years=2)

    if dissolution_date < now:
        msg.append({'error': _('Dissolution delay date must be in the future'), 'path': dissolution_date_path})
        return msg

    if dissolution_date > two_years:
        msg.append({'error': _('Dissolution delay date must not exceed two years'), 'path': dissolution_date_path})
        return msg
    

    return None