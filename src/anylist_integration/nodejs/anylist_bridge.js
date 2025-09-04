#!/usr/bin/env node

/**
 * AnyList Bridge - Node.js script to interact with AnyList API
 * This script is called from Python with command-line arguments
 */

// Handle self-signed certificates (common in corporate environments)
process.env["NODE_TLS_REJECT_UNAUTHORIZED"] = 0;

// Suppress console output from the anylist package
const originalConsoleLog = console.log;
const originalConsoleError = console.error;

// Temporarily override console methods to suppress library output
function suppressOutput() {
    console.log = () => {};
    console.error = () => {};
}

// Restore console methods for our output
function restoreOutput() {
    console.log = originalConsoleLog;
    console.error = originalConsoleError;
}

const AnyList = require('anylist');
const fs = require('fs').promises;
const path = require('path');

// Parse command line arguments
const args = process.argv.slice(2);
const command = args[0];

// Credentials file path
const CREDS_FILE = path.join(__dirname, '..', '..', 'data', 'anylist_nodejs_session.json');

/**
 * Load credentials from file
 */
async function loadCredentials() {
    try {
        const data = await fs.readFile(CREDS_FILE, 'utf8');
        return JSON.parse(data);
    } catch (error) {
        // Silently fail - credentials file may not exist on first run
        return null;
    }
}

/**
 * Save credentials to file
 */
async function saveCredentials(creds) {
    try {
        await fs.writeFile(CREDS_FILE, JSON.stringify(creds, null, 2));
        return true;
    } catch (error) {
        // Silently fail
        return false;
    }
}

/**
 * Login to AnyList
 */
async function login(email, password) {
    try {
        suppressOutput();
        const any = new AnyList({ email, password });
        
        await any.login();
        
        // Save session for future use
        const credentials = {
            email: email,
            lastLogin: new Date().toISOString()
        };
        await saveCredentials(credentials);
        
        // Cleanup
        any.teardown();
        
        restoreOutput();
        console.log(JSON.stringify({ 
            success: true, 
            message: 'Successfully logged in to AnyList' 
        }));
    } catch (error) {
        restoreOutput();
        console.error(JSON.stringify({ 
            success: false, 
            error: error.message 
        }));
        process.exit(1);
    }
}

/**
 * Fetch all recipes
 */
async function fetchRecipes(email, password) {
    try {
        suppressOutput();
        const any = new AnyList({ email, password });
        
        await any.login();
        
        // Get all recipes
        const recipes = await any.getRecipes();
        
        // Get user data which includes recipe collections
        const userData = await any._getUserData();
        const recipeCollections = userData.recipeDataResponse.recipeCollections || [];
        
        // Create a map of recipe IDs to their collection data (names and IDs)
        const recipeToCollections = {};
        recipeCollections.forEach(collection => {
            if (collection.recipeIds && collection.recipeIds.length > 0) {
                collection.recipeIds.forEach(recipeId => {
                    if (!recipeToCollections[recipeId]) {
                        recipeToCollections[recipeId] = [];
                    }
                    recipeToCollections[recipeId].push({
                        id: collection.identifier,
                        name: collection.name,
                        timestamp: collection.timestamp
                    });
                });
            }
        });
        
        // Format recipes for Python
        const formattedRecipes = recipes.map(recipe => {
            // Enhanced photo handling - check both photoUrls and photoIds
            let photoInfo = { hasPhoto: false };
            
            if (recipe.photoUrls && recipe.photoUrls.length > 0) {
                // Direct photo URLs available
                photoInfo = {
                    hasPhoto: true,
                    url: recipe.photoUrls[0],
                    urls: recipe.photoUrls,
                    source: 'direct'
                };
            } else if (recipe.photoIds && recipe.photoIds.length > 0) {
                // Construct photo URLs using AnyList's CDN pattern
                const constructedUrls = recipe.photoIds.map(photoId => 
                    `https://photos.anylist.com/${photoId}.jpg`
                );
                
                photoInfo = {
                    hasPhoto: true,
                    url: constructedUrls[0],
                    urls: constructedUrls,
                    photoIds: recipe.photoIds,
                    source: 'constructed'
                };
            }

            return {
                id: recipe.identifier,
                name: recipe.name || 'Untitled Recipe',
                description: recipe.note || '',
                prep_time: recipe.prepTime || 0,
                cook_time: recipe.cookTime || 0,
                servings: recipe.servings || '',
                rating: recipe.rating || 0,
                source: recipe.sourceName || '',
                sourceUrl: recipe.sourceUrl || '',
                createdAt: recipe.creationTimestamp ? new Date(recipe.creationTimestamp * 1000).toISOString() : null,
                updatedAt: recipe.timestamp ? new Date(recipe.timestamp * 1000).toISOString() : null,
                scaleFactor: recipe.scaleFactor || 1, // Default to 1x scaling
                collections: recipeToCollections[recipe.identifier] || [],
                ingredients: (recipe.ingredients || []).map(ing => ({
                    name: ing.name || ing.rawIngredient || '',
                    quantity: ing.quantity || '',
                    note: ing.note || '',
                    rawText: ing.rawIngredient || ''
                })),
                preparation_steps: recipe.preparationSteps || [],
                nutritional_info: recipe.nutritionalInfo || '',
                photo: photoInfo,
                // Additional metadata for debugging
                raw_fields: {
                    hasPhotoIds: !!(recipe.photoIds && recipe.photoIds.length > 0),
                    hasPhotoUrls: !!(recipe.photoUrls && recipe.photoUrls.length > 0),
                    adCampaignId: recipe.adCampaignId,
                    paprikaIdentifier: recipe.paprikaIdentifier
                }
            };
        });
        
        // Cleanup
        any.teardown();
        
        restoreOutput();
        console.log(JSON.stringify({
            success: true,
            recipes: formattedRecipes,
            count: formattedRecipes.length
        }));
    } catch (error) {
        restoreOutput();
        console.error(JSON.stringify({
            success: false,
            error: error.message,
            recipes: []
        }));
        process.exit(1);
    }
}

/**
 * Fetch recipe by ID
 */
async function fetchRecipeById(email, password, recipeId) {
    try {
        suppressOutput();
        const any = new AnyList({ email, password });
        
        await any.login();
        
        // Get all recipes and find the specific one
        const recipes = await any.getRecipes();
        const recipe = recipes.find(r => r.identifier === recipeId);
        
        if (!recipe) {
            restoreOutput();
            console.log(JSON.stringify({
                success: false,
                error: 'Recipe not found'
            }));
            process.exit(1);
        }
        
        // Get user data which includes recipe collections
        const userData = await any._getUserData();
        const recipeCollections = userData.recipeDataResponse.recipeCollections || [];
        
        // Find collections this recipe belongs to
        const collections = [];
        recipeCollections.forEach(collection => {
            if (collection.recipeIds && collection.recipeIds.includes(recipeId)) {
                collections.push({
                    id: collection.identifier,
                    name: collection.name,
                    timestamp: collection.timestamp
                });
            }
        });
        
        // Enhanced photo handling - check both photoUrls and photoIds
        let photoInfo = { hasPhoto: false };
        
        if (recipe.photoUrls && recipe.photoUrls.length > 0) {
            // Direct photo URLs available
            photoInfo = {
                hasPhoto: true,
                url: recipe.photoUrls[0],
                urls: recipe.photoUrls,
                source: 'direct'
            };
        } else if (recipe.photoIds && recipe.photoIds.length > 0) {
            // Construct photo URLs using AnyList's CDN pattern
            const constructedUrls = recipe.photoIds.map(photoId => 
                `https://photos.anylist.com/${photoId}.jpg`
            );
            
            photoInfo = {
                hasPhoto: true,
                url: constructedUrls[0],
                urls: constructedUrls,
                photoIds: recipe.photoIds,
                source: 'constructed'
            };
        }

        const formattedRecipe = {
            id: recipe.identifier,
            name: recipe.name || 'Untitled Recipe',
            description: recipe.note || '',
            prep_time: recipe.prepTime || 0,
            cook_time: recipe.cookTime || 0,
            servings: recipe.servings || '',
            rating: recipe.rating || 0,
            source: recipe.sourceName || '',
            sourceUrl: recipe.sourceUrl || '',
            createdAt: recipe.creationTimestamp ? new Date(recipe.creationTimestamp * 1000).toISOString() : null,
            updatedAt: recipe.timestamp ? new Date(recipe.timestamp * 1000).toISOString() : null,
            scaleFactor: recipe.scaleFactor || 1, // Default to 1x scaling
            collections: collections,
            ingredients: (recipe.ingredients || []).map(ing => ({
                name: ing.name || ing.rawIngredient || '',
                quantity: ing.quantity || '',
                note: ing.note || '',
                rawText: ing.rawIngredient || ''
            })),
            preparation_steps: recipe.preparationSteps || [],
            nutritional_info: recipe.nutritionalInfo || '',
            photo: photoInfo,
            // Additional metadata for debugging
            raw_fields: {
                hasPhotoIds: !!(recipe.photoIds && recipe.photoIds.length > 0),
                hasPhotoUrls: !!(recipe.photoUrls && recipe.photoUrls.length > 0),
                adCampaignId: recipe.adCampaignId,
                paprikaIdentifier: recipe.paprikaIdentifier
            }
        };
        
        // Cleanup
        any.teardown();
        
        restoreOutput();
        console.log(JSON.stringify({
            success: true,
            recipe: formattedRecipe
        }));
    } catch (error) {
        restoreOutput();
        console.error(JSON.stringify({
            success: false,
            error: error.message
        }));
        process.exit(1);
    }
}

/**
 * Get shopping lists
 */
async function getLists(email, password) {
    try {
        suppressOutput();
        const any = new AnyList({ email, password });
        
        await any.login();
        
        const lists = await any.getLists();
        
        const formattedLists = lists.map(list => ({
            id: list.identifier,
            name: list.name,
            itemCount: list.items ? list.items.length : 0
        }));
        
        // Cleanup
        any.teardown();
        
        restoreOutput();
        console.log(JSON.stringify({
            success: true,
            lists: formattedLists
        }));
    } catch (error) {
        restoreOutput();
        console.error(JSON.stringify({
            success: false,
            error: error.message,
            lists: []
        }));
        process.exit(1);
    }
}

/**
 * Get recipe collections
 */
async function getCollections(email, password) {
    try {
        suppressOutput();
        const any = new AnyList({ email, password });
        
        await any.login();
        
        // Get user data which includes recipe collections
        const userData = await any._getUserData();
        const recipeCollections = userData.recipeDataResponse.recipeCollections || [];
        
        // Format collections for Python
        const formattedCollections = recipeCollections.map(collection => ({
            id: collection.identifier,
            name: collection.name,
            recipeIds: collection.recipeIds || [],
            recipeCount: (collection.recipeIds || []).length,
            timestamp: collection.timestamp ? new Date(collection.timestamp * 1000).toISOString() : null
        }));
        
        // Cleanup
        any.teardown();
        
        restoreOutput();
        console.log(JSON.stringify({
            success: true,
            collections: formattedCollections,
            count: formattedCollections.length
        }));
    } catch (error) {
        restoreOutput();
        console.error(JSON.stringify({
            success: false,
            error: error.message,
            collections: []
        }));
        process.exit(1);
    }
}


/**
 * Create a new recipe
 */
async function createRecipe(email, password, recipeData) {
    try {
        suppressOutput();
        const any = new AnyList({ email, password });
        
        await any.login();
        
        // Parse recipe data if it's a string
        if (typeof recipeData === 'string') {
            recipeData = JSON.parse(recipeData);
        }
        
        const newRecipe = await any.createRecipe({
            name: recipeData.name,
            note: recipeData.description || '',
            preparationSteps: recipeData.preparation_steps || [],
            servings: recipeData.servings || '',
            sourceName: recipeData.source || '',
            sourceUrl: recipeData.sourceUrl || '',
            scaleFactor: 1,
            rating: recipeData.rating || 0,
            ingredients: (recipeData.ingredients || []).map(ing => ({
                rawIngredient: ing.rawText || `${ing.quantity} ${ing.name}`.trim(),
                name: ing.name,
                quantity: ing.quantity || '',
                note: ing.note || ''
            })),
            nutritionalInfo: recipeData.nutritional_info || '',
            cookTime: recipeData.cook_time || 0,
            prepTime: recipeData.prep_time || 0,
            creationTimestamp: Date.now() / 1000,
            timestamp: Date.now() / 1000
        });
        
        await newRecipe.save();
        
        // Cleanup
        any.teardown();
        
        restoreOutput();
        console.log(JSON.stringify({
            success: true,
            recipe: {
                id: newRecipe.identifier,
                name: newRecipe.name
            }
        }));
    } catch (error) {
        restoreOutput();
        console.error(JSON.stringify({
            success: false,
            error: error.message
        }));
        process.exit(1);
    }
}

// Main execution
async function main() {
    if (!command) {
        console.error(JSON.stringify({
            success: false,
            error: 'No command specified'
        }));
        process.exit(1);
    }
    
    switch (command) {
        case 'login':
            if (args.length < 3) {
                console.error(JSON.stringify({
                    success: false,
                    error: 'Email and password required'
                }));
                process.exit(1);
            }
            await login(args[1], args[2]);
            break;
            
        case 'fetch-recipes':
            if (args.length < 3) {
                console.error(JSON.stringify({
                    success: false,
                    error: 'Email and password required'
                }));
                process.exit(1);
            }
            await fetchRecipes(args[1], args[2]);
            break;
            
        case 'fetch-recipe':
            if (args.length < 4) {
                console.error(JSON.stringify({
                    success: false,
                    error: 'Email, password, and recipe ID required'
                }));
                process.exit(1);
            }
            await fetchRecipeById(args[1], args[2], args[3]);
            break;
            
        case 'get-lists':
            if (args.length < 3) {
                console.error(JSON.stringify({
                    success: false,
                    error: 'Email and password required'
                }));
                process.exit(1);
            }
            await getLists(args[1], args[2]);
            break;
            
        case 'get-collections':
            if (args.length < 3) {
                console.error(JSON.stringify({
                    success: false,
                    error: 'Email and password required'
                }));
                process.exit(1);
            }
            await getCollections(args[1], args[2]);
            break;
            
        case 'create-recipe':
            if (args.length < 4) {
                console.error(JSON.stringify({
                    success: false,
                    error: 'Email, password, and recipe data required'
                }));
                process.exit(1);
            }
            await createRecipe(args[1], args[2], args[3]);
            break;
            
        default:
            console.error(JSON.stringify({
                success: false,
                error: `Unknown command: ${command}`
            }));
            process.exit(1);
    }
}

// Run main function
main().catch(error => {
    console.error(JSON.stringify({
        success: false,
        error: error.message
    }));
    process.exit(1);
});
