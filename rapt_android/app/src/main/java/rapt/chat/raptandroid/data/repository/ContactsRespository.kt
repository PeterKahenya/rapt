package rapt.chat.raptandroid.data.repository

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
    suspend fun uploadPhoneContacts(phoneContacts: List<PhoneContact>): List<APIContact>
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

    override suspend fun uploadPhoneContacts(phoneContacts: List<PhoneContact>): List<APIContact> {
        val auth = authRepository.auth() ?: throw Exception("No Auth")
        val apiRequestContacts = mutableListOf<APIContactUpload>()
        for (phoneContact in phoneContacts){
            if (phoneContact.phone != auth.phone){
                apiRequestContacts.add(
                    APIContactUpload(name = phoneContact.name, phone = phoneContact.phone)
                )
            }
        }
        return api.addContacts(
            accessToken = "Bearer ${auth.accessToken}",
            userId = auth.userId,
            addContactsRequest = apiRequestContacts
        )
    }

    override suspend fun saveContacts(contacts: List<APIContact>) {
        for (apiContact in contacts){
            val dbContact = contactDao.getByPhone(apiContact.phone)
            if (dbContact != null){
                dbContact.isActive = apiContact.isActive
                dbContact.name = apiContact.name
                dbContact.contactId = apiContact.contactId
                contactDao.update(dbContact)
            } else {
                contactDao.insert(
                    Contact(
                        name = apiContact.name,
                        phone = apiContact.phone,
                        contactId = apiContact.contactId,
                        isActive = apiContact.isActive
                    )
                )
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
        val auth = authRepository.auth() ?: throw Exception("No Auth")
        return api.getContacts(
            accessToken = "Bearer ${auth.accessToken}",
            userId = auth.userId
        )
    }
}