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
"""Test suite to ensure Voluntary Dissolution is validated correctly."""
import copy
from datetime import datetime, timedelta
from http import HTTPStatus
from unittest.mock import patch

import pytest
from registry_schemas.example_data import FILING_HEADER, DELAY_DISSOLUTION, SPECIAL_RESOLUTION
from reportlab.lib.pagesizes import letter

from legal_api.models import Business
from legal_api.services import MinioService
from legal_api.services.filings.validations import delay_dissolution
from legal_api.services.filings.validations.delay_dissolution import validate
from tests.unit.services.filings.test_utils import _upload_file
from tests.unit.services.filings.validations import lists_are_equal
from datetime import datetime
from dateutil.relativedelta import relativedelta


@pytest.mark.parametrize(
    'test_status, admin_freeze, expected_code, expected_msg',
    [
        ('SUCCESS', False, None, None),
        ('SUCCESS', None, None, None),
        ('FAIL', True, HTTPStatus.BAD_REQUEST, 'Dissolution cannot be delayed on frozen businesses.')
    ]
)

def test_status_not_frozen(session, test_status, admin_freeze, expected_code, expected_msg):
    """Assert that the number of delays can be validated."""
    # setup
    business = Business(identifier='BC1234567', admin_freeze=admin_freeze)
    now = datetime.now().date()
    one_year = now + relativedelta(years=1)

    filing = copy.deepcopy(FILING_HEADER)
    filing['filing']['header']['name'] = 'delayDissolution'
    filing['filing']['delayDissolution'] = copy.deepcopy(DELAY_DISSOLUTION)
    filing['filing']['delayDissolution']['dissolutionDate'] = f"{one_year}"
    filing['filing']['delayDissolution']['parties'][1]['deliveryAddress'] = \
        filing['filing']['delayDissolution']['parties'][1]['mailingAddress']
    
  
    #with patch.object(delay_dissolution, 'validate_affidavit', return_value=None):
    err = validate(business, filing)

    # validate outcomes
    if expected_code or expected_msg:
        assert expected_code == err.code
        assert expected_msg == err.msg[0]['error']
    else:
        assert not err

@pytest.mark.parametrize(
    'test_status, number_of_delays, expected_code, expected_msg',
    [
        ('SUCCESS', 0, None, None),
        ('SUCCESS', 1, None, None),
        ('FAIL', 2, HTTPStatus.BAD_REQUEST, 'Dissolution may only be delayed twice'),
        ('FAIL', 3, HTTPStatus.BAD_REQUEST, 'Dissolution may only be delayed twice')
    ]
)

def test_number_of_dissolution_delays(session, test_status, number_of_delays, expected_code, expected_msg):
    """Assert that the number of delays can be validated."""
    # setup
    business = Business(identifier='BC1234567')
    now = datetime.now().date()
    one_year = now + relativedelta(years=1)

    filing = copy.deepcopy(FILING_HEADER)
    filing['filing']['header']['name'] = 'delayDissolution'
    filing['filing']['delayDissolution'] = copy.deepcopy(DELAY_DISSOLUTION)
    filing['filing']['delayDissolution']['dissolutionDate'] = f"{one_year}"
    filing['filing']['delayDissolution']['numberOfDelays'] = number_of_delays
    filing['filing']['delayDissolution']['parties'][1]['deliveryAddress'] = \
        filing['filing']['delayDissolution']['parties'][1]['mailingAddress']
    
  
    #with patch.object(delay_dissolution, 'validate_affidavit', return_value=None):
    err = validate(business, filing)

    # validate outcomes
    if expected_code or expected_msg:
        assert expected_code == err.code
        assert expected_msg == err.msg[0]['error']
    else:
        assert not err


now = datetime.now().date()
one_year_ago = now + relativedelta(years=-1)
one_year = now + relativedelta(years=1)
two_years = now + relativedelta(years=2)
three_years = now + relativedelta(years=3)

@pytest.mark.parametrize(
    'test_status, dissolutionDate, expected_code, expected_msg',
    [
        ('FAIL', one_year_ago, HTTPStatus.BAD_REQUEST, 'Dissolution delay date must be in the future'),
        ('SUCCESS', now, None, None),
        ('SUCCESS', one_year, None, None),
        ('SUCCESS', two_years, None, None),
        ('FAIL', three_years, HTTPStatus.BAD_REQUEST, 'Dissolution delay date must not exceed two years')
    ]
)

def test_delay_dissolution_dates(session, test_status, dissolutionDate, expected_code, expected_msg):
    """Assert that the number of delays can be validated."""
    # setup
    business = Business(identifier='BC1234567')
 
    filing = copy.deepcopy(FILING_HEADER)
    filing['filing']['header']['name'] = 'delayDissolution'
    filing['filing']['delayDissolution'] = copy.deepcopy(DELAY_DISSOLUTION)
    filing['filing']['delayDissolution']['dissolutionDate'] = f"{dissolutionDate}"
    filing['filing']['delayDissolution']['parties'][1]['deliveryAddress'] = \
        filing['filing']['delayDissolution']['parties'][1]['mailingAddress']
    
  
    #with patch.object(delay_dissolution, 'validate_affidavit', return_value=None):
    err = validate(business, filing)

    # validate outcomes
    if expected_code or expected_msg:
        assert expected_code == err.code
        assert expected_msg == err.msg[0]['error']
    else:
        assert not err