package rapt.chat.raptandroid.data.repository

import android.provider.ContactsContract.CommonDataKinds.Phone
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import rapt.chat.raptandroid.data.model.APIContact
import rapt.chat.raptandroid.data.source.APIContactUpload
import rapt.chat.raptandroid.data.source.Contact
import rapt.chat.raptandroid.data.source.ContactDao
import rapt.chat.raptandroid.data.source.PhoneContact
import rapt.chat.raptandroid.data.source.RaptApi
import rapt.chat.raptandroid.data.source.RaptContentProvider
import javax.inject.Inject

interface ContactsRepository{
    suspend fun getAllDBContacts(): List<Contact>
    suspend fun getPhoneContacts(): List<PhoneContact>
    suspend fun uploadContacts(contacts: List<PhoneContact>): List<APIContact>
    suspend fun saveContacts(contacts: List<APIContact>)
    suspend fun searchContacts(query: String): List<Contact>
    suspend fun deleteContact(contact: Contact)
    suspend fun apiFetchContacts(): List<APIContact>
}

class ContactsRepositoryImpl @Inject constructor(
    private val api: RaptApi,
    private val contactDao: ContactDao,
    private val contentProvider: RaptContentProvider,
    private val authRepository: AuthRepository
) : ContactsRepository{

    override suspend fun getAllDBContacts(): List<Contact> {
        return contactDao.getAll()
    }

    override suspend fun getPhoneContacts(): List<PhoneContact> {
        return contentProvider.getContacts()
    }

    override suspend fun uploadContacts(contacts: List<PhoneContact>): List<APIContact> {
        val auth = authRepository.auth()


        if (auth != null){
            val apiRequestContacts = mutableListOf<APIContactUpload>()
            for (contact in contacts){
                if (contact.phone != auth.phone){
                    apiRequestContacts.add(
                        APIContactUpload(
                            name = contact.name,
                            phone = contact.phone
                        )
                    )
                }
            }
            println("UserId: ${auth.userId}")
            println("Uploading contacts: $apiRequestContacts")
            return api.addContacts(
                accessToken = "Bearer ${auth.accessToken}",
                userId = auth.userId,
                addContactsRequest = apiRequestContacts
            )
        } else {
            throw Exception("No auth")
        }
    }
    override suspend fun saveContacts(contacts: List<APIContact>) {
        for (apiContact in contacts){
            val dbContact = contactDao.getByPhone(apiContact.phone)
            if (dbContact.isEmpty()){
                contactDao.insert(
                    Contact(
                        name = apiContact.name,
                        phone = apiContact.phone,
                        contactId = apiContact.contactId,
                        userId = apiContact.userId,
                        isActive = apiContact.isActive
                    )
                )
            }else{
                dbContact[0].isActive = apiContact.isActive
                dbContact[0].name = apiContact.name
                dbContact[0].userId = apiContact.userId
                dbContact[0].contactId = apiContact.contactId
                contactDao.update(dbContact[0])
            }
        }
    }

    override suspend fun searchContacts(query: String): List<Contact> {
        return contactDao.search(query)
    }
    override suspend fun deleteContact(contact: Contact) {
        contactDao.delete(contact)
    }

    override suspend fun apiFetchContacts(): List<APIContact> {
        val auth = authRepository.auth()
        if (auth != null){
            return api.getContacts(
                accessToken = "Bearer ${auth.accessToken}",
                userId = auth.userId,
                )
        } else {
            throw Exception("No auth")
        }
    }
}