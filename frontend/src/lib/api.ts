import axios from 'axios';
import { toast } from "sonner";

const api = axios.create({
    baseURL: 'https://jsonplaceholder.typicode.com', // для теста
})

api.interceptors.response.use(
    response => response,
    error => {
        // Глобальный перехват ошибок
        const message = error.response?.data?.message ?? `Ошибка запроса: ${error.message}`;
        toast.error('Что-то пошло не так', { description: message });
        return Promise.reject(error);
    }
)

export default api;