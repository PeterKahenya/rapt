package rapt.chat.raptandroid.domain.use_case

import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import rapt.chat.raptandroid.common.Resource
import rapt.chat.raptandroid.data.model.ProfileResponse
import rapt.chat.raptandroid.data.model.ProfileUpdateRequest
import rapt.chat.raptandroid.domain.repository.ProfileRepository
import retrofit2.HttpException
import java.io.IOException
import javax.inject.Inject

class ProfileUpdateUseCase @Inject constructor(
    private val profileRepository: ProfileRepository
){
    suspend operator fun invoke(profileUpdateRequest: ProfileUpdateRequest): Flow<Resource<ProfileResponse>> = flow {
        try {
            emit(Resource.Loading())
            val profileUpdateResponse: ProfileResponse = profileRepository.updateProfile(profileUpdateRequest)
            println("ProfileUpdateUseCase: $profileUpdateResponse")
            emit(Resource.Success(profileUpdateResponse))
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