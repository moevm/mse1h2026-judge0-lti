import ErrorPage from '../ErrorPage/ErrorPage'

const NotFoundPage = () => (
    <ErrorPage
        code={404}
        title="Страница не найдена"
        description="Возможно, она была удалена или никогда не существовала"
        icon="🧭"
    />
)

export default NotFoundPage