const NotFoundPage = () => {

    return (
        <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-[#1e1e1e]">
            <button className="text-white bg-linear-to-r from-blue-500 via-blue-600 to-blue-700 hover:bg-linear-to-br focus:ring-4 focus:outline-none focus:ring-blue-300 dark:focus:ring-blue-800 shadow-lg shadow-blue-500/50 dark:shadow-lg dark:shadow-blue-800/80 font-medium rounded-md text-sm px-4 py-2.5 text-center leading-5">hello button</button>
            <div className="bg-red-500 text-white p-8 text-2xl">
                Tailwind works
            </div>
        </div>
    )
}

export default NotFoundPage