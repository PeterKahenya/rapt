package rapt.chat.raptandroid.data.source

import android.content.Context
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
import rapt.chat.raptandroid.data.model.Auth
import rapt.chat.raptandroid.dataStore

interface RaptDataStore{
    suspend fun saveAuth(auth: Auth)
    suspend fun getAuth(): Auth?
}

class RaptDataStoreImpl(val context: Context): RaptDataStore {

    private val accessTokenKey = stringPreferencesKey("access_token")
    private val phoneKey = stringPreferencesKey("phone")

    override suspend fun saveAuth(auth: Auth) {
        context.dataStore.edit { settings ->
            settings[accessTokenKey] = auth.accessToken
            settings[phoneKey] = auth.phone
        }
    }

    override suspend fun getAuth(): Auth? {
        val accessToken: Flow<Auth?> = context.dataStore.data.map { preferences ->
            println("getAuth: $preferences")
            preferences[accessTokenKey]?.let { preferences[phoneKey]?.let { it1 -> Auth(it, it1) } }
        }
        return accessToken.first()
    }

}