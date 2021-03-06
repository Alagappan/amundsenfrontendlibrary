import { SagaIterator } from 'redux-saga';
import { call, put, takeEvery } from 'redux-saga/effects';

import { GetCurrentUser } from './reducer';
import { getCurrentUser } from './api';

export function* getUserWorker(): SagaIterator {
  try {
    const user = yield call(getCurrentUser);
    yield put({ type: GetCurrentUser.SUCCESS, payload: user });
  } catch (e) {
    yield put({ type: GetCurrentUser.FAILURE });
  }
}

export function* getCurrentUserWatcher(): SagaIterator {
  yield takeEvery(GetCurrentUser.ACTION, getUserWorker);
}
