import { useState, useEffect } from 'react';
import { supabase } from './supabaseClient';
import { BookOpen, Share2, Search, TrendingUp } from 'lucide-react';

function App() {
  const [activeTab, setActiveTab] = useState('catalogs');
  const [catalogs, setCatalogs] = useState([]);
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  async function fetchData() {
    setLoading(true);
    
    // Récupération des catalogues
    const { data: catData, error: catErr } = await supabase
      .from('catalogs')
      .select('*, competitors(name)')
      .order('created_at', { ascending: false });
      
    if (catErr) console.error("Erreur Catalogues:", catErr);
    if (catData) setCatalogs(catData);

    // Récupération des posts
    const { data: postData, error: postErr } = await supabase
      .from('social_posts')
      .select('*, competitors(name)')
      .order('published_at', { ascending: false });
      
    if (postErr) console.error("Erreur Posts:", postErr);
    if (postData) setPosts(postData);
    
    setLoading(false);
  }

  useEffect(() => {
    fetchData();
  }, []);

  // Filtrage selon le terme recherché
  const filteredCatalogs = catalogs.filter(c => 
    c.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.competitors?.name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredPosts = posts.filter(p => 
    p.content_text?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.competitors?.name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="flex h-screen bg-gray-100 font-sans text-gray-800">
      {/* Menu Latéral */}
      <aside className="w-64 bg-white border-r shadow-sm flex flex-col">
        <div className="p-6 border-b">
          <h1 className="text-2xl font-bold text-blue-600">U-Veille SaaS</h1>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          <button 
            onClick={() => setActiveTab('catalogs')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition ${activeTab === 'catalogs' ? 'bg-blue-50 text-blue-700 font-semibold' : 'hover:bg-gray-50'}`}
          >
            <BookOpen size={20} /> Catalogues Bonial
          </button>
          <button 
            onClick={() => setActiveTab('social')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition ${activeTab === 'social' ? 'bg-blue-50 text-blue-700 font-semibold' : 'hover:bg-gray-50'}`}
          >
            <Share2 size={20} /> Réseaux Sociaux
          </button>
        </nav>
      </aside>

      {/* Contenu Principal */}
      <main className="flex-1 p-8 overflow-y-auto">
        <header className="flex justify-between items-center mb-8">
          <h2 className="text-3xl font-bold">
            {activeTab === 'catalogs' ? 'Veille Catalogues (Bonial)' : 'Veille Réseaux Sociaux'}
          </h2>
          <div className="relative">
             <Search className="absolute left-3 top-2.5 text-gray-400" size={20} />
             <input 
              type="text" 
              placeholder="Rechercher..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 border rounded-lg focus:outline-blue-500 bg-white" 
             />
          </div>
        </header>

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <p className="text-gray-500 animate-pulse">Chargement des données Supabase...</p>
          </div>
        ) : (
          <>
            {/* Vue Catalogues */}
            {activeTab === 'catalogs' && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredCatalogs.length === 0 ? (
                  <div className="col-span-full p-8 text-center bg-white rounded-xl border">
                    <p className="text-gray-500">Aucun catalogue trouvé.</p>
                  </div>
                ) : filteredCatalogs.map((catalog) => (
                  <div key={catalog.id} className="bg-white rounded-xl shadow-sm border overflow-hidden hover:shadow-md transition">
                    <img src={catalog.cover_image_url || 'https://via.placeholder.com/400x300?text=Pas+d+image'} alt="Couverture" className="w-full h-48 object-cover border-b" />
                    <div className="p-4">
                      <span className="text-xs font-bold uppercase text-blue-600 bg-blue-50 px-2 py-1 rounded-full">
                        {catalog.competitors?.name || 'Concurrent'}
                      </span>
                      <h3 className="mt-2 font-bold text-lg">{catalog.title}</h3>
                      <p className="text-sm text-gray-500 mt-1">Du {catalog.valid_from} au {catalog.valid_to}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Vue Réseaux Sociaux */}
            {activeTab === 'social' && (
              <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-gray-50 border-b">
                      <th className="p-4 font-semibold text-gray-600">Concurrent</th>
                      <th className="p-4 font-semibold text-gray-600">Plateforme</th>
                      <th className="p-4 font-semibold text-gray-600">Date</th>
                      <th className="p-4 font-semibold text-gray-600">Likes</th>
                      <th className="p-4 font-semibold text-gray-600">Contenu</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredPosts.length === 0 ? (
                      <tr>
                        <td colSpan="5" className="p-8 text-center text-gray-500">
                          Aucun post trouvé.
                        </td>
                      </tr>
                    ) : filteredPosts.map((post) => (
                      <tr key={post.id} className="border-b hover:bg-gray-50">
                        <td className="p-4 font-medium">{post.competitors?.name}</td>
                        <td className="p-4">
                          <span className="px-2 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-800">
                            {post.platform}
                          </span>
                        </td>
                        <td className="p-4 text-sm">{post.published_at}</td>
                        <td className="p-4 text-sm font-semibold flex items-center gap-1">
                          <TrendingUp size={16} className="text-green-500"/> {post.likes_count}
                        </td>
                        <td className="p-4 text-sm text-gray-600 truncate max-w-xs">{post.content_text}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}

export default App;