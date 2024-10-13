package rapt.chat.raptandroid.data.repository

import rapt.chat.raptandroid.common.Constants
import rapt.chat.raptandroid.data.model.Auth
import rapt.chat.raptandroid.data.model.LoginResponse
import rapt.chat.raptandroid.data.model.RefreshResponse
import rapt.chat.raptandroid.data.model.VerifyResponse
import rapt.chat.raptandroid.data.source.RaptApi
import rapt.chat.raptandroid.data.source.RaptDataStore
import javax.inject.Inject

interface AuthRepository {
    suspend fun auth(): Auth?
    suspend fun login(phone: String, clientId: String, clientSecret: String): LoginResponse
    suspend fun verify(phoneVerificationCode: String, phone: String, clientId: String, clientSecret: String): VerifyResponse
    suspend fun refresh(accessToken: String, clientId: String, clientSecret: String): RefreshResponse
}

class AuthRepositoryImpl @Inject constructor(
    private val api: RaptApi,
    private val ds: RaptDataStore
): AuthRepository {

    override suspend fun auth(): Auth? {
//        println("Auth")
        val localAuth = ds.getAuth()
        if (localAuth != null){
            if (localAuth.isExpired()){
                val refreshResponse = refresh(
                    accessToken = localAuth.accessToken,
                    clientId = Constants.CLIENT_APP_ID,
                    clientSecret = Constants.CLIENT_APP_SECRET
                )
                val profileResponse = api.getProfile("Bearer ${refreshResponse.accessToken}")
                val newAuth = Auth(
                    accessToken = refreshResponse.accessToken,
                    phone = profileResponse.phone,
                    userId = profileResponse.id,
                    expiresAt = System.currentTimeMillis() + (refreshResponse.expiresIn * 60*1000)
                )
                ds.saveAuth(newAuth)
                return newAuth
            }else{
                return localAuth
            }
        }else{
            return null
        }
    }

    override suspend fun login(phone: String, clientId: String, clientSecret: String): LoginResponse {
        println("AuthRepositoryImpl Login Request: $phone $clientId $clientSecret")
        return api.login(phone, clientId, clientSecret)
    }

    override suspend fun verify(phoneVerificationCode: String, phone: String, clientId: String, clientSecret: String): VerifyResponse {
        println("AuthRepositoryImpl Verify Request: $phoneVerificationCode $phone $clientId $clientSecret")
        val verifyResponse = api.verify(phoneVerificationCode, phone, clientId, clientSecret)
        println("AuthRepositoryImpl Verify Response: $verifyResponse")
        val profileResponse = api.getProfile("Bearer ${verifyResponse.accessToken}")
        ds.saveAuth(Auth(
            accessToken = verifyResponse.accessToken,
            phone = phone,
            userId = profileResponse.id,
            expiresAt = System.currentTimeMillis() + (verifyResponse.expiresIn * 60 * 1000)
        ))
        println("AuthRepositoryImpl Verify Saved Auth: ${ds.getAuth()}")
        return verifyResponse
    }

    override suspend fun refresh(accessToken: String, clientId: String, clientSecret: String): RefreshResponse {
        println("AuthRepositoryImpl Refresh: $accessToken $clientId $clientSecret")
        val refreshResponse =  api.refresh(accessToken = accessToken, clientId = clientId, clientSecret = clientSecret)
        return refreshResponse
    }
}