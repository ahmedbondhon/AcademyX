import api from './axios'

export const authApi = {
  login:    (data)  => api.post('/auth/login', data),
  register: (data)  => api.post('/auth/register', data),
}

export const obeApi = {
  getCOAttainment:    (courseId) => api.get(`/obe/co-attainment/${courseId}`),
  getPOAttainment:    (programId) => api.get(`/obe/po-attainment/${programId}`),
  getCourseSummary:   (courseId) => api.get(`/obe/course-summary/${courseId}`),
  getMyCourses:       ()          => api.get('/obe/my-courses'),
  getAllCourses:       ()          => api.get('/obe/all-courses'),
  getCourseRisk:      (courseId) => api.get(`/obe/risk/${courseId}`),
  getMyRisk:          (courseId) => api.get(`/obe/my-risk/${courseId}`),
  getMyBreakdown:     (courseId) => api.get(`/obe/student-breakdown/${courseId}`),
}

export const alertApi = {
  preview: (courseId) => api.get(`/alerts/preview/${courseId}`),
  trigger: (courseId) => api.post(`/alerts/trigger/${courseId}?dry_run=false`),
}

export const uploadApi = {
  uploadMarksheet: (file, save = false) => {
    const form = new FormData()
    form.append('file', file)
    return api.post(`/upload/marksheet?save=${save}`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  downloadTemplate: (courseId) =>
    api.get(`/upload/template/${courseId}`, { responseType: 'blob' }),
}

export const reportApi = {
  downloadOBEReport: (courseId) =>
    api.get(`/reports/obe/${courseId}`, { responseType: 'blob' }),
}