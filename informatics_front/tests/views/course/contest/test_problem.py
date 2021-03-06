import io
import pytest

from unittest.mock import patch

from flask import g, url_for

DEFAULT_PAGE = 1
DEFAULT_COUNT = 10


@pytest.mark.problem
def test_problem(client, problem, authorized_user):
    url = url_for('contest.problem', problem_id=problem.id)
    resp = client.get(url)
    assert resp.status_code == 200

    content = resp.json
    assert 'data' in content

    content = content['data']
    assert content.get('id') == problem.id

    for field in ('content', 'description', 'memorylimit', 'name', 'output_only', 'timelimit',):
        assert getattr(problem, field) == content.get(field, -1)  # avoid None is None comparison


#     Добавить ассерт на сэмплы


@pytest.mark.problem
def test_get_problem_submission(client, authorized_user, problem, ):
    with patch('informatics_front.internal_rmatics.get_runs_filter') as get_runs_filter:
        get_runs_filter.return_value = ({}, 200)

        url = url_for('contest.submissions', problem_id=problem.id, page=DEFAULT_PAGE, )
        resp = client.get(url)
        assert resp.status_code == 200
        get_runs_filter.assert_called_with(problem.id, {'page': DEFAULT_PAGE, 'count': DEFAULT_COUNT}, is_admin=False)


@pytest.mark.problem
def test_post_problem_submission(client, authorized_user, problem, ):
    with patch('informatics_front.internal_rmatics.send_submit') as send_submit, \
            patch('webargs.flaskparser.parser.parse_files') as parse_files:
        send_submit.return_value = ({}, 200)
        parse_files.return_value = True

        data = {
            'statement_id': 1,
            'lang_id': 2,
        }

        url = url_for('contest.submissions', problem_id=problem.id)
        data['file'] = io.BytesIO(b'sample data'), 'test.cpp'
        resp = client.post(url, data=data)
        assert resp.status_code == 200
        send_submit.assert_called_with(True, g.user['id'], problem.id, 1, 2, )
        send_submit.reset_mock()

        # statement_id is an optional argument
        del data['statement_id']
        data['file'] = io.BytesIO(b'sample data'), 'test.cpp'
        url = url_for('contest.submissions', problem_id=problem.id)
        resp = client.post(url, data=data)
        assert resp.status_code == 200
        send_submit.assert_called_with(True, g.user['id'], problem.id, None, 2, )
