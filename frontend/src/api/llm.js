import request from './request'

export const llmStatus = () => request.get('/llm/status')
export const reviewRecord = (recordId) => request.post('/llm/review', { recordId })
