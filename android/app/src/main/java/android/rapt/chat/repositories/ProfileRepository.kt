package android.rapt.chat.repositories

import android.rapt.chat.models.ProfileUpdateRequest
import android.rapt.chat.models.User
import android.rapt.chat.sources.RaptAPI
import javax.inject.Inject

interface ProfileRepository {
    suspend fun getProfile(): User
    suspend fun updateProfile(
        userId: String,
        profileUpdateRequest: ProfileUpdateRequest
    ): User
}

class ProfileRepositoryImpl @Inject constructor(
    private val api: RaptAPI,
    private val authRepository: AuthRepository
) : ProfileRepository{

    override suspend fun getProfile(): User {
        val auth = authRepository.auth()
        return api.getProfile(accessToken = "Bearer ${auth?.accessToken}")
    }

    override suspend fun updateProfile(
        userId: String,
        profileUpdateRequest: ProfileUpdateRequest
    ): User {
        val auth = authRepository.auth()
        return api.updateProfile(
            userId,
            accessToken = "Bearer ${auth?.accessToken}",
            profileUpdateRequest = profileUpdateRequest
        )
    }

}