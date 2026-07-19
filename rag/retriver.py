class Retriver:
    @staticmethod
    def create_retriver(vector_store):
        return vector_store.as_retriever(
            search_kwargs={'K':4}
        )