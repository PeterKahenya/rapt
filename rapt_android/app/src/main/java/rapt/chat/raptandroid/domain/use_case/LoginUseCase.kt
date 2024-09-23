package rapt.chat.raptandroid.domain.use_case

import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import rapt.chat.raptandroid.common.Resource
import rapt.chat.raptandroid.data.model.LoginRequest
import rapt.chat.raptandroid.data.model.LoginResponse
import rapt.chat.raptandroid.domain.repository.AuthRepository
import retrofit2.HttpException
import java.io.IOException
import javax.inject.Inject

class LoginUseCase @Inject constructor(
    private val authRepository: AuthRepository
) {
    operator fun invoke(loginRequest: LoginRequest): Flow<Resource<LoginResponse>> = flow {
        try {
            emit(Resource.Loading())
            val loginResponse: LoginResponse = authRepository.login(loginRequest)
            println("LoginUseCase: $loginResponse")
            emit(Resource.Success(loginResponse))
        } catch (e: HttpException) {
            println("HttpException: ${e.response()}")
            emit(Resource.Error(e.localizedMessage ?: "An unexpected error occurred"))
        } catch (e: IOException) {
            println("IOException: ${e.localizedMessage}")
            emit(
                Resource.Error(
                    e.localizedMessage ?: "Couldn't reach server. Check your internet connection"
                )
            )
        }catch (e: java.lang.SecurityException){
            println("SecurityException: ${e.localizedMessage}")
            emit(Resource.Error(e.localizedMessage ?: "An unexpected error occurred"))
        }
    }
}