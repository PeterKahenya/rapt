package rapt.chat.raptandroid.data.repository

import rapt.chat.raptandroid.data.model.ProfileResponse
import rapt.chat.raptandroid.data.model.ProfileUpdateRequest
import rapt.chat.raptandroid.data.source.api.RaptApi
import rapt.chat.raptandroid.domain.repository.ProfileRepository
import javax.inject.Inject

class ProfileRepositoryImpl @Inject constructor(
    private val api: RaptApi
): ProfileRepository {
    override suspend fun getProfile(accessToken: String): ProfileResponse {
        return api.getProfile(accessToken = "Bearer $accessToken")
    }

    override suspend fun updateProfile(
        accessToken: String,
        profileUpdateRequest: ProfileUpdateRequest
    ): ProfileResponse {
        return api.updateProfile(accessToken = "Bearer $accessToken", profileUpdateRequest = profileUpdateRequest)
    }
}