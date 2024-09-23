package rapt.chat.raptandroid.domain.use_case

import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import rapt.chat.raptandroid.common.Resource
import rapt.chat.raptandroid.data.model.VerifyRequest
import rapt.chat.raptandroid.data.model.VerifyResponse
import rapt.chat.raptandroid.domain.repository.AuthRepository
import retrofit2.HttpException
import java.io.IOException
import javax.inject.Inject

class VerifyPhoneUseCase @Inject constructor(
    private val authRepository: AuthRepository
) {
    operator fun invoke(verifyRequest: VerifyRequest): Flow<Resource<VerifyResponse>> = flow {
        try {
            emit(Resource.Loading())
            val verifyResponse: VerifyResponse = authRepository.verify(verifyRequest)
            emit(Resource.Success(verifyResponse))
        } catch (e: HttpException) {
            emit(Resource.Error(e.localizedMessage ?: "An unexpected error occurred"))
        } catch (e: IOException) {
            emit(
                Resource.Error(
                    e.localizedMessage ?: "Couldn't reach server. Check your internet connection"
                )
            )
        }
    }
}