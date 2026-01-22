import { createStore } from 'vuex'

export default createStore({
  state: {
    diaries: []
  },
  mutations: {
    ADD_DIARY(state, diary) {
      state.diaries.push({
        ...diary,
        id: Date.now(),
        date: new Date().toISOString().substr(0, 10)
      })
    }
  },
  actions: {
    addDiary({ commit }, diary) {
      // 여기서 감정분석 API를 호출할 수 있습니다
      commit('ADD_DIARY', diary)
    }
  },
  getters: {
    getAllDiaries: state => state.diaries
  }
})