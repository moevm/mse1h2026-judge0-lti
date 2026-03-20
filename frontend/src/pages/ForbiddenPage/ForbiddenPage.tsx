import ErrorPage from '../ErrorPage/ErrorPage'

const ForbiddenPage = () => (
    <ErrorPage
        code={403}
        title="Доступ запрещён"
        description="У вас нет прав для просмотра этой страницы"
        icon="🔒"
    />
)

export default ForbiddenPage