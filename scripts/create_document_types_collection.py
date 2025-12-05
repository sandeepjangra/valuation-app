#!/usr/bin/env python3
"""
Create document_types collection and migrate existing document fields
"""
import os
import sys
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

# Add the backend directory to the path to import modules
sys.path.append('/Users/sandeepjangra/Downloads/development/ValuationAppV1/backend')

def get_mongodb_connection():
    """Get MongoDB connection"""
    try:
        # Try to get connection from environment or use default
        mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
        client = MongoClient(mongo_uri)
        db = client['valuation_admin']
        return db
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None

def create_document_types_collection(db):
    """Create the document_types collection with initial data"""
    
    # Documents extracted from current templates (in order as requested)
    document_types = [
        {
            "documentId": "agreement_to_sell",
            "uiDisplayName": "Agreement To Sell",
            "fieldType": "textarea",
            "placeholder": "Enter Agreement to Sell details, if any",
            "applicablePropertyTypes": ["Land", "Apartment", "House"],
            "applicableBanks": ["SBI", "HDFC", "ICICI", "AXIS", "PNB", "*"], # * means all banks
            "sortOrder": 1,
            "isRequired": False,
            "includeInCustomTemplate": True,
            "isActive": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "documentId": "list_of_documents_produced",
            "uiDisplayName": "List of documents produced",
            "fieldType": "textarea",
            "placeholder": "Enter List of documents provided, if any",
            "applicablePropertyTypes": ["Land", "Apartment", "House"],
            "applicableBanks": ["*"],
            "sortOrder": 2,
            "isRequired": False,
            "includeInCustomTemplate": True,
            "isActive": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "documentId": "allotment_letter",
            "uiDisplayName": "Allotment Letter",
            "fieldType": "textarea",
            "placeholder": "Enter Allotment Letter details, if any",
            "applicablePropertyTypes": ["Land", "Apartment"],
            "applicableBanks": ["*"],
            "sortOrder": 3,
            "isRequired": False,
            "includeInCustomTemplate": True,
            "isActive": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "documentId": "layout_plan",
            "uiDisplayName": "Layout Plan",
            "fieldType": "textarea",
            "placeholder": "Enter Layout Plan details, if any",
            "applicablePropertyTypes": ["Land", "Apartment"],
            "applicableBanks": ["*"],
            "sortOrder": 4,
            "isRequired": False,
            "includeInCustomTemplate": True,
            "isActive": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "documentId": "sales_deed",
            "uiDisplayName": "Sales Deed",
            "fieldType": "textarea",
            "placeholder": "Enter Sales Deed details, if any",
            "applicablePropertyTypes": ["Land", "Apartment", "House"],
            "applicableBanks": ["*"],
            "sortOrder": 5,
            "isRequired": False,
            "includeInCustomTemplate": True,
            "isActive": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "documentId": "title_deed",
            "uiDisplayName": "Title Deed",
            "fieldType": "textarea",
            "placeholder": "Enter Title Deed details, if any",
            "applicablePropertyTypes": ["Land", "Apartment", "House"],
            "applicableBanks": ["*"],
            "sortOrder": 6,
            "isRequired": False,
            "includeInCustomTemplate": True,
            "isActive": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "documentId": "mortgage_deed",
            "uiDisplayName": "Mortgage Deed",
            "fieldType": "textarea",
            "placeholder": "Enter Mortgage Deed details, if any",
            "applicablePropertyTypes": ["Land", "Apartment", "House"],
            "applicableBanks": ["*"],
            "sortOrder": 7,
            "isRequired": False,
            "includeInCustomTemplate": True,
            "isActive": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "documentId": "chain_of_documents",
            "uiDisplayName": "Chain of Documents",
            "fieldType": "textarea",
            "placeholder": "Enter Chain of Documents details, if any",
            "applicablePropertyTypes": ["Land", "Apartment", "House"],
            "applicableBanks": ["*"],
            "sortOrder": 8,
            "isRequired": False,
            "includeInCustomTemplate": True,
            "isActive": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "documentId": "property_card",
            "uiDisplayName": "Property Card",
            "fieldType": "textarea",
            "placeholder": "Enter Property Card details, if any",
            "applicablePropertyTypes": ["Land", "Apartment", "House"],
            "applicableBanks": ["*"],
            "sortOrder": 9,
            "isRequired": False,
            "includeInCustomTemplate": True,
            "isActive": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "documentId": "mutation_records",
            "uiDisplayName": "Mutation Records",
            "fieldType": "textarea",
            "placeholder": "Enter Mutation Records details, if any",
            "applicablePropertyTypes": ["Land", "Apartment", "House"],
            "applicableBanks": ["*"],
            "sortOrder": 10,
            "isRequired": False,
            "includeInCustomTemplate": True,
            "isActive": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
    ]
    
    try:
        # Drop existing collection if it exists
        if 'document_types' in db.list_collection_names():
            print("⚠️ Dropping existing document_types collection...")
            db.document_types.drop()
        
        # Create the collection and insert documents
        result = db.document_types.insert_many(document_types)
        print(f"✅ Created document_types collection with {len(result.inserted_ids)} documents")
        
        # Create indexes for better performance
        db.document_types.create_index("documentId", unique=True)
        db.document_types.create_index("applicablePropertyTypes")
        db.document_types.create_index("applicableBanks")
        db.document_types.create_index("isActive")
        print("✅ Created indexes for document_types collection")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating document_types collection: {e}")
        return False

def update_templates_to_use_document_reference(db):
    """Update existing templates to use document collection reference"""
    
    try:
        # Get all template collections
        collections = [name for name in db.list_collection_names() 
                      if name.endswith('_property_details') or 
                         name.endswith('_land_property_details') or
                         name.endswith('_apartment_property_details')]
        
        updated_count = 0
        
        for collection_name in collections:
            collection = db[collection_name]
            
            # Find all documents in this collection
            templates = collection.find({})
            
            for template in templates:
                modified = False
                
                if 'documents' in template:
                    for document in template['documents']:
                        if 'sections' in document:
                            for section in document['sections']:
                                # Check if this is a document section (contains agreement_to_sell, etc.)
                                if (section.get('sectionName', '').lower().find('document') != -1 or 
                                    section.get('sectionId', '').lower().find('document') != -1 or
                                    any(field.get('fieldId') in ['agreement_to_sell', 'list_of_documents_produced', 
                                                                'allotment_letter', 'layout_plan', 'sales_deed'] 
                                        for field in section.get('fields', []))):
                                    
                                    # Replace fields with document collection reference
                                    section['useDocumentCollection'] = True
                                    section['documentFilter'] = {
                                        'propertyType': template.get('propertyType', 'Land'),
                                        'bankCode': template.get('bankCode', '*')
                                    }
                                    
                                    # Keep original fields as backup for now
                                    section['originalFields'] = section.get('fields', [])
                                    
                                    # Remove fields array - will be populated by aggregation
                                    if 'fields' in section:
                                        del section['fields']
                                    
                                    modified = True
                                    print(f"📝 Updated section '{section['sectionName']}' in template {document.get('templateName', 'Unknown')}")
                
                if modified:
                    # Update the document in MongoDB
                    collection.replace_one({'_id': template['_id']}, template)
                    updated_count += 1
        
        print(f"✅ Updated {updated_count} templates to use document collection reference")
        return True
        
    except Exception as e:
        print(f"❌ Error updating templates: {e}")
        return False

def main():
    """Main execution function"""
    print("🚀 Starting Document Types Collection Creation and Migration...")
    
    # Get database connection
    db = get_mongodb_connection()
    if db is None:
        print("❌ Failed to connect to database")
        return False
    
    print(f"📊 Connected to database: {db.name}")
    
    # Step 1: Create document_types collection
    print("\n📋 Step 1: Creating document_types collection...")
    if not create_document_types_collection(db):
        return False
    
    # Step 2: Update templates to use document collection
    print("\n🔄 Step 2: Updating templates to use document collection reference...")
    if not update_templates_to_use_document_reference(db):
        return False
    
    print("\n✅ Migration completed successfully!")
    print("📌 Next steps:")
    print("   1. Update backend aggregation logic to merge document_types")
    print("   2. Test existing endpoints to ensure compatibility")
    print("   3. Update frontend to handle new document structure")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)