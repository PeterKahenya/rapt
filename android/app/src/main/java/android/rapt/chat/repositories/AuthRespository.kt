package android.rapt.chat.data.repositories

import android.rapt.chat.common.RaptConstants
import android.rapt.chat.data.models.Auth
import android.rapt.chat.data.models.LoginRequest
import android.rapt.chat.data.models.LoginResponse
import android.rapt.chat.data.models.RefreshRequest
import android.rapt.chat.data.models.RefreshResponse
import android.rapt.chat.data.models.VerifyRequest
import android.rapt.chat.data.models.VerifyResponse
import android.rapt.chat.data.models.toFieldMap
import android.rapt.chat.data.sources.RaptAPI
import android.rapt.chat.data.sources.RaptDatastore

interface AuthRepository {
    suspend fun auth(): Auth?
    suspend fun login(loginRequest: LoginRequest): LoginResponse
    suspend fun verify(verifyRequest: VerifyRequest): VerifyResponse
    suspend fun refresh(refreshRequest: RefreshRequest): RefreshResponse
}

class AuthRepositoryImpl(
    private val api: RaptAPI, private val ds: RaptDatastore
) : AuthRepository {
    override suspend fun auth(): Auth? {
        val localAuth = ds.getAuth()
        if (localAuth != null) {
            if (localAuth.isExpired()) {
                val refreshRequest = RefreshRequest(
                    accessToken = localAuth.accessToken,
                    clientId = RaptConstants.CLIENT_APP_ID,
                    clientSecret = RaptConstants.CLIENT_APP_SECRET
                )
                val refreshResponse = refresh(refreshRequest)
                val user = api.getProfile("Bearer ${refreshResponse.accessToken}")
                val newAuth = Auth(
                    accessToken = refreshResponse.accessToken,
                    phone = user.phone,
                    userId = user.id,
                    expiresAt = System.currentTimeMillis() + (refreshResponse.expiresIn * 1000)
                )
                ds.saveAuth(newAuth)
                return newAuth
            } else {
                return localAuth
            }
        } else {
            return null
        }
    }

    override suspend fun login(loginRequest: LoginRequest): LoginResponse {
        return api.login(loginRequest.toFieldMap())
    }

    override suspend fun verify(verifyRequest: VerifyRequest): VerifyResponse {
        val verifyResponse = api.verify(verifyRequest.toFieldMap())
        val user = api.getProfile("Bearer ${verifyResponse.accessToken}")
        ds.saveAuth(Auth(
            accessToken = verifyResponse.accessToken,
            phone = user.phone,
            userId = user.id,
            expiresAt = System.currentTimeMillis() + (verifyResponse.expiresIn * 60 * 1000)
        ))
        return verifyResponse
    }

    override suspend fun refresh(refreshRequest: RefreshRequest): RefreshResponse {
        return api.refresh(refreshRequest.toFieldMap())
    }
}