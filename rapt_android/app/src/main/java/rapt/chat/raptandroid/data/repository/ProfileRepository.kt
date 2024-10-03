package rapt.chat.raptandroid.data.repository

import rapt.chat.raptandroid.data.model.ProfileResponse
import rapt.chat.raptandroid.data.model.ProfileUpdateRequest
import rapt.chat.raptandroid.data.source.RaptApi
import javax.inject.Inject

interface ProfileRepository {
    suspend fun getProfile(): ProfileResponse
    suspend fun updateProfile(
        userId: String,
        profileUpdateRequest: ProfileUpdateRequest
    ): ProfileResponse
}

class ProfileRepositoryImpl @Inject constructor(
    private val api: RaptApi,
    private val authRepository: AuthRepository
) : ProfileRepository {

    override suspend fun getProfile(): ProfileResponse {
        val auth = authRepository.auth()
        return api.getProfile(accessToken = "Bearer ${auth?.accessToken}")
    }

    override suspend fun updateProfile(
        userId: String,
        profileUpdateRequest: ProfileUpdateRequest
    ): ProfileResponse {
        val auth = authRepository.auth()
        return api.updateProfile(
            userId,
            accessToken = "Bearer ${auth?.accessToken}",
            profileUpdateRequest = profileUpdateRequest
        )
    }
}