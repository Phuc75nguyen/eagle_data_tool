// Function will replace the default fetch() function of the browser
export const fetchWithAuth = async (url: string, options: RequestInit = {}) => {
     // 1. Always automatically insert "credentials: 'include'" to get the Cookie
     const finalOptions: RequestInit = {
          ...options,
          credentials: "include",
     };

     // 2. Perform API call normally
     let response = await fetch(url, finalOptions);

     // 3. IF 401 Unauthorized -> Start the hidden magic trick
     if (response.status === 401) {
          try {
               // Secretly bring Refresh Token (cookie) to request new Access Token
               const refreshRes = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/refresh`, {
                    method: "POST",
                    credentials: "include", // Must bring cookie
               });

               if (refreshRes.ok) {
                    // Success! Got a brand new 15-minute Access Token.
                    // Immediately call the API that just failed (so the user doesn't know anything)
                    response = await fetch(url, finalOptions);
               } else {
                    // Refresh Token 7 days is also expired -> No way to save.
                    // Clear all displayed information and redirect to Login page
                    sessionStorage.clear();
                    window.location.href = "/"; // Or the path to the Login page
               }
          } catch (error) {
               // Network error -> Kick user out for safety
               sessionStorage.clear();
               window.location.href = "/";
          }
     }

     // Return the final result (success) to the Component to handle next
     return response;
};