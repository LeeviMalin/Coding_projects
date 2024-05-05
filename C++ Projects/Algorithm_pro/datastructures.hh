// Code given from the course at the beginning

#ifndef DATASTRUCTURES_HH
#define DATASTRUCTURES_HH

#include <string>
#include <vector>
#include <tuple>
#include <utility>
#include <limits>
#include <functional>
#include <exception>
#include <cmath>

#include <unordered_map>
#include <map>
#include <utility>
#include <stack>

// Types for IDs
using StationID = std::string;
using TrainID = std::string;
using RegionID = unsigned long long int;
using Name = std::string;
using Time = unsigned short int;

// Return values for cases where required thing was not found
StationID const NO_STATION = "---";
TrainID const NO_TRAIN = "---";
RegionID const NO_REGION = -1;
Name const NO_NAME = "!NO_NAME!";
Time const NO_TIME = 9999;

// Return value for cases where integer values were not found
int const NO_VALUE = std::numeric_limits<int>::min();


// Type for a coordinate (x, y)
struct Coord
{
    int x = NO_VALUE;
    int y = NO_VALUE;
};

// Example: Defining == and hash function for Coord so that it can be used
// as key for std::unordered_map/set, if needed
inline bool operator==(Coord c1, Coord c2) { return c1.x == c2.x && c1.y == c2.y; }
inline bool operator!=(Coord c1, Coord c2) { return !(c1==c2); } // Not strictly necessary

struct CoordHash
{
    std::size_t operator()(Coord xy) const
    {
        auto hasher = std::hash<int>();
        auto xhash = hasher(xy.x);
        auto yhash = hasher(xy.y);
        // Combine hash values (magic!)
        return xhash ^ (yhash + 0x9e3779b9 + (xhash << 6) + (xhash >> 2));
    }
};

// Example: Defining < for Coord so that it can be used
// as key for std::map/set
inline bool operator<(Coord c1, Coord c2)
{
    if (pow(c1.y,2)+pow(c1.x,2) < pow(c2.y,2)+pow(c2.x,2)) { return true; }

    else if (pow(c2.y,2)+pow(c2.x,2) < pow(c1.y,2)+pow(c1.x,2)) { return false; }

    else { return c1.y < c2.y; }
}

// Return value for cases where coordinates were not found
Coord const NO_COORD = {NO_VALUE, NO_VALUE};

// Type for a distance (in metres)
using Distance = int;

// Return value for cases where Distance is unknown
Distance const NO_DISTANCE = NO_VALUE;

// This exception class is there just so that the user interface can notify
// about operations which are not (yet) implemented
class NotImplemented : public std::exception
{
public:
    NotImplemented() : msg_{} {}
    explicit NotImplemented(std::string const& msg) : msg_{msg + " not implemented"} {}

    virtual const char* what() const noexcept override
    {
        return msg_.c_str();
    }
private:
    std::string msg_;
};


// This is the class you are supposed to implement

class Datastructures
{
public:
    Datastructures();
    ~Datastructures();

    // Estimate of performance: O(1)
    // Short rationale for estimate: Funkiton size dokumentiaation
    // mukaan sen tehokkuus on vakio.
    unsigned int station_count();

    // Estimate of performance: O(1)
    // Short rationale for estimate: Funkiton clear dokumentiaation
    // mukaan sen tehokkuus on vakio.
    void clear_all();

    // Estimate of performance: O(n)
    // Short rationale for estimate: Funktiossa käydään läpi kaikki mapin alkiot kerran
    // ja niitä käsitellään vakio aikaisilla funktioilla.
    std::vector<StationID> all_stations();

    // Estimate of performance: O(log(n))
    // Short rationale for estimate: mappiin lisääminen on
    // keskimäärin log n, muut operaatiot vakioaikaisia
    bool add_station(StationID id, Name const& name, Coord xy);

    // Estimate of performance: O(n)
    // Short rationale for estimate:  count ja at ovat O(n),
    // mutta keskimäärin vakioaikaisia
    Name get_station_name(StationID id);

    // Estimate of performance: O(n)
    // Short rationale for estimate: count ja at ovat O(n),
    // mutta keskimäärin vakioaikaisia
    Coord get_station_coordinates(StationID id);

    // We recommend you implement the operations below only after implementing the ones above

    // Estimate of performance: O(n)
    // Short rationale for estimate: kaikki mapin alkiot käydään läpi kerran
    // pushback on vakioaikainen
    std::vector<StationID> stations_alphabetically();

    // Estimate of performance: O(n)
    // Short rationale for estimate: kaikki mapin alkiot käydään läpi kerran
    // pushback on vakioaikainen
    std::vector<StationID> stations_distance_increasing();

    // Estimate of performance: O(n)
    // Short rationale for estimate: at ja count on O(n) ja keskimäärin vakio
    StationID find_station_with_coord(Coord xy);

    // Estimate of performance: O(n)
    // Short rationale for estimate: at ja count on O(n) ja keskimäärin vakio
    bool change_station_coord(StationID id, Coord newcoord);

    // Estimate of performance: O(n)
    // Short rationale for estimate: Unordered mappiin lisääminen ja count on O(n)
    // ja keskimäärin vakio
    bool add_departure(StationID stationid, TrainID trainid, Time time);

    // Estimate of performance: O(n)
    // Short rationale for estimate: erase ja count on O(n) ja keskimäärin vakio
    bool remove_departure(StationID stationid, TrainID trainid, Time time);

    // Estimate of performance: O(n log(n))
    // Short rationale for estimate: kaikki alkiot käydään läpi
    // kerran ja sortataan minkä tehokkuus on n log(n)
    std::vector<std::pair<Time, TrainID>> station_departures_after(StationID stationid, Time time);

    // We recommend you implement the operations below only after implementing the ones above

    // Estimate of performance: O(n)
    // Short rationale for estimate: count on O(n) ja
    // rakenteeseen lisääminen on keskimääein vakio
    bool add_region(RegionID id, Name const& name, std::vector<Coord> coords);

    // Estimate of performance: O(n)
    // Short rationale for estimate: kaikki alkiot käydään kerran läpi
    // ja pushback on keskimäärin vakio
    std::vector<RegionID> all_regions();

    // Estimate of performance: O(n)
    // Short rationale for estimate: Tiedon hakeminen mapista avaimella ja count
    // on O(n) ja keskimäärin vakio
    Name get_region_name(RegionID id);

    // Estimate of performance: O(n)
    // Short rationale for estimate: Tiedon hakeminen mapista avaimella ja count
    // on O(n) ja keskimäärin vakio
    std::vector<Coord> get_region_coords(RegionID id);

    // Estimate of performance: O(n)
    // Short rationale for estimate: count on O(n) ja
    // rakenteeseen lisääminen on keskimääein vakio
    bool add_subregion_to_region(RegionID id, RegionID parentid);

    // Estimate of performance: O(n)
    // Short rationale for estimate: count ja rakenteeseen lisääminen
    // ovat O(n) ja keskimäärin vakioita
    bool add_station_to_region(StationID id, RegionID parentid);

    // Estimate of performance: O(n)
    // Short rationale for estimate: kaikki parentit käydään läpi
    // count ja at ovat O(n) ja keskimäärin vakioita
    std::vector<RegionID> station_in_regions(StationID id);

    // Non-compulsory operations

    // Estimate of performance: O(n)
    // Short rationale for estimate: count on O(n) ja subRegions käy
    // kaikki alkiot kerran läpi
    std::vector<RegionID> all_subregions_of_region(RegionID id);

    // Estimate of performance:
    // Short rationale for estimate:
    std::vector<StationID> stations_closest_to(Coord xy);

    // Estimate of performance: O(n)
    // Short rationale for estimate: kaikki alkiot käydään kolmeen kertaan läpi
    // joten funktio on hidas. Muut operaattorit ovat O(n) ja keskimäärin
    // vakioaikaisia
    bool remove_station(StationID id);

    // Estimate of performance: O(n^2)
    // Short rationale for estimate: kaikki alkiot käydään läpi kahteen
    // kertaan ja sisäkkäisten forlooppien tehokkuus on O(n)
    RegionID common_parent_of_regions(RegionID id1, RegionID id2);

    //
    // New assignment 2 operations
    //

    // Estimate of performance: O(n)
    // Short rationale for estimate: kaikki alkiot
    // käydään kerran läpi while loopilla
    bool add_train(TrainID trainid, std::vector<std::pair<StationID, Time>> stationtimes);

    // Estimate of performance: O(n)
    // Short rationale for estimate: kaikki aseman naapurit käydään läpi for loopilla
    std::vector<StationID> next_stations_from(StationID id);

    // Estimate of performance: O(n)
    // Short rationale for estimate: vaikka algoritmissä on kaksi sisäkkäistä loppia
    // ne käyvät jokaisessa tapauksessa vain kerran kaikki alkiot läpi
    std::vector<StationID> train_stations_from(StationID stationid, TrainID trainid);

    // Estimate of performance: O(n)
    // Short rationale for estimate: käy kaikki asemat läpi for loopilla
    void clear_trains();

    // Estimate of performance: O(n^2)
    // Short rationale for estimate: alkoioita käydään läpi kahdella sisäkkäisellä loopilla
    std::vector<std::pair<StationID, Distance>> route_any(StationID fromid, StationID toid);

    // Non-compulsory operations

    // Estimate of performance:
    // Short rationale for estimate:
    std::vector<std::pair<StationID, Distance>> route_least_stations(StationID fromid, StationID toid);

    // Estimate of performance:
    // Short rationale for estimate:
    std::vector<StationID> route_with_cycle(StationID fromid);

    // Estimate of performance:
    // Short rationale for estimate:
    std::vector<std::pair<StationID, Distance>> route_shortest_distance(StationID fromid, StationID toid);

    // Estimate of performance:
    // Short rationale for estimate:
    std::vector<std::pair<StationID, Time>> route_earliest_arrival(StationID fromid, StationID toid, Time starttime);

private:
    struct stationInfo
    {
        Name name = NO_NAME;
        Coord coordinates = NO_COORD;
        std::unordered_map<TrainID,Time> trainList;
        RegionID parentRegion = NO_REGION;
        std::unordered_map<StationID,Distance> neighbours;
        // 0 = musta
        // 1 = harmaa
        // 2 = valkoinen
        int colour = 2;
        std::pair<StationID,Distance> from = {NO_STATION,NO_DISTANCE};
    };
    struct regionInfo {
        std::vector<Coord> area;
        std::vector<StationID> stations;
        std::vector<RegionID> subRegions;
        RegionID parentRegion = NO_REGION;
        Name name;
    };
    struct trainInfo
    {
        std::vector<std::pair<StationID,Time>> stations;
    };


    //Containers for regions and stations
    std::unordered_map<StationID,stationInfo> stationList;
    std::unordered_map<RegionID,regionInfo> regionList;
    std::unordered_map<TrainID,trainInfo> trainList;
    //Containers for helping certain methods
    std::map<Coord,StationID> distanceFirst;
    std::map<Name,StationID> nameFirst;

    // Containers helping private funtions 
    std::vector<RegionID> subregs;
    std::vector<RegionID> pregs;
    std::vector<std::pair<StationID,Distance>> route;
    

    // Functions gets all parents for region and saves vector of them 
    // to the classes containers
    // This is questionable solution but it works
    void parentRegions(RegionID);
    // Same as function above but for subregions of a regions
    void subRegions(RegionID);
    
    void trackRoute(std::pair<StationID,Distance>);
    // Sets staions white
    void setWhite();
};

#endif // DATASTRUCTURES_HH
