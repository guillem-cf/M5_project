import os
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import average_precision_score, precision_recall_curve,accuracy_score
import torch
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt



def plot_embeddings_ImageText(image_embeddings, text_embeddinfs, title, output_path, xlim=None, ylim=None):

    plt.figure(figsize=(10, 10))
    
    plt.scatter(image_embeddings[:, 0], image_embeddings[:, 1], alpha=0.5, color='blue')
    plt.scatter(text_embeddinfs[:, 0], text_embeddinfs[:, 1], alpha=0.5, color='pink')
    if xlim:
        plt.xlim(xlim[0], xlim[1])
    if ylim:
        plt.ylim(ylim[0], ylim[1])
    plt.title(title)
    
    path = os.path.join(output_path, title)
    plt.savefig(path)
    plt.close()
    


def extract_embeddings_image(dataloader, model, device, dim_features = 2048):
    with torch.no_grad():
        model.eval()
        embeddings = np.zeros((len(dataloader.dataset), dim_features))
        labels = np.zeros(len(dataloader.dataset))
        k = 0
        for images, target in tqdm(dataloader):
            if torch.cuda.is_available():
                images = images.to(device)
            embeddings[k:k + images.shape[0]] = model.get_embedding_image(images).data.cpu().numpy()
            labels[k:k + images.shape[0]] = target.numpy()
            k += images.shape[0]
    return embeddings, labels


def extract_embeddings_text(dataloader, model, device, network_text, dim_features=2048):
    with torch.no_grad():
        model.eval()
        embeddings = np.zeros((len(dataloader.dataset), dim_features))
        labels = np.zeros(len(dataloader.dataset))
        k = 0
        for captions, target in tqdm(dataloader):
            if 
            # if torch.cuda.is_available():
            #     NO PODEM PASSAR CAPTIONS A GPU PERQUE NO ES UN TENSOR
            embeddings[k:k + len(captions)] = model.get_embedding_text(captions).data.cpu().numpy()
            labels[k:k + len(captions)] = target.numpy()
            k += len(captions)
    return embeddings, labels


def plot_PR_multiclass (classes, labels, y_score_knn,path):
    precision = dict()
    recall = dict()
    for i in range(len(classes)):
        labels_val = np.where(labels == i, 1, 0)
        ap = round(average_precision_score(labels_val,  y_score_knn[:, i]),2)
        #append the average precision for each class rounded to 2 decimals
        precision[i], recall[i], _ = precision_recall_curve(labels_val, y_score_knn[:, i])
        plt.plot(recall[i], precision[i], lw=2, label='{} {},'.format(classes[i], ap))
        
    plt.xlabel("recall")
    plt.ylabel("precision")
    plt.legend(loc="best")
    plt.title("precision vs. recall curve")

    plt.savefig(path + "/PrecisionRecallCurve.png")
    plt.close()
    
    
    
def plot_PR_binary(results, path):
    precision, recall = precisionRecall(results) 
    plt.figure(figsize=(10, 10))
    plt.plot(recall, precision, lw=2)
    # Set the x and y axis limits accordingly to the data
    
    x_min, x_max = 0, 1
    y_min , y_max = 0, 1
    
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    
    plt.xlabel("recall")
    plt.ylabel("precision")
    plt.savefig(path + "/PrecisionRecallCurve.png")
    plt.close()


def calculate_APs (y_true_test, y_true_test_repeated, neigh_labels, neigh_dist):
    for k in [1, 3, 5, 10, 20, 30]:
        prec_at_k = accuracy_score(y_true_test_repeated[:, 0:k].flatten(), neigh_labels[:, 0:k].flatten())
        print("Prec@" + str(k) + ":", prec_at_k)

    aps_all = []
    aps_5 = []
    for i in range(neigh_labels.shape[0]):
        aps_all.append(average_precision_score((neigh_labels[i] == y_true_test[i]).astype(int), -neigh_dist[i]))
        aps_5.append(average_precision_score((neigh_labels[i, 0:5] == y_true_test[i]).astype(int), -neigh_dist[i, 0:5]))
    mAP_all = np.mean(aps_all)
    mAP_5 = np.mean(aps_5)

    print("mAP@all:", mAP_all)
    print("mAP@5:", mAP_5)
    
    
def calculate_APs_coco (results, path, wandb=None):
    results_txt = []
    for k in [1, 3, 5]:
        prec_at_k = mPrecisionK(results, k)
        if wandb is not None:
            wandb.log({"Prec@" + str(k): prec_at_k})
        print("Prec@" + str(k) + ":", prec_at_k)
        results_txt.append("Prec@" + str(k) + ": " + str(prec_at_k))

    map_value = MAP(results)
    print("mAP:", map)
    results_txt.append("mAP: " + str(map))
    if wandb is not None:
        wandb.log({"mAP": map})
    
    # Save results in .txt file
    with open(path + "/results.txt", "w") as output:
        output.write(str(results_txt))
        
    return map_value
    
    
    
    
def positives_ImageToText(neighbors_index, neighbors_id, databaseDataset, queryDataset):
    #query is the image
    
    resultsQueries = []
    
    for i_query in tqdm(range(neighbors_id.shape[0])):
        resultQuery = []
        
        # Això esta bé, torna les captions correctament de cada imatge del dataset
        queryCaptions = queryDataset.getCaptionsId_fromImageIdx(i_query)
        
        # image, image_id = queryDataset[i_query]
        
        # captions_strings = [databaseDataset[databaseDataset.getCaptionIdx_fromId(capt)] for capt in queryCaptions]
        
        for i_db in range(neighbors_id.shape[1]):
            
            caption_id = neighbors_id[i_query, i_db]
            # caption_idx = neighbors_index[i_query, i_db]
            
            # caption, caption_id_prova = databaseDataset[caption_idx]
            
            # imageDB_id = databaseDataset.getImageId_fromCaptionIdx(caption_idx)[0]
            # imageDB_idx = queryDataset.getImageIdx_fromId(imageDB_id)
            
            # imageDB, imageDB_id = queryDataset[imageDB_idx]
            
            if caption_id in queryCaptions: 
                resultQuery.append(1)
            else:
                resultQuery.append(0)
        
        resultsQueries.append(resultQuery)
    
    return np.array(resultsQueries)

def positives_ImageToText_old(neighbors, databaseDataset, queryDataset):
    #query is the image
    
    resultsQueries = []
    
    for i_query in tqdm(range(neighbors.shape[0])):
        resultQuery = []
        
        queryCaptions = queryDataset.getCaptions(i_query)
        
        for i_db in range(neighbors.shape[1]):
            
            dbIndex = neighbors[i_query, i_db]
            
            caption = databaseDataset.getCaptionId(dbIndex)
            
            if caption in queryCaptions: 
                resultQuery.append(1)
            else:
                resultQuery.append(0)
        
        resultsQueries.append(resultQuery)
    
    return np.array(resultsQueries)


def precisionK(results, k):
    """
    This function computes the precision@k for a query
    giving the positive results
    Parameters
    ----------
    results : numpy array
        Array with 1 when retrive was positive, 0 otherwise.
    k : int
        k value to compute.
    Returns
    -------
    float
        p@k value.
    """
    
    return np.sum(results[:k])/k

def mPrecisionK(listResults, k):
    """
    This function computes the mean precision@k over all the queries.
    Parameters
    ----------
    listResults : numpy array
        For each query (row), 1 if retrieve was positive 0 otherwise.
    k : int
        k value to compute.
    Returns
    -------
    float
        Mean p@k value.
    """
    
    valSum = 0
    
    for i in range(listResults.shape[0]):
        valSum += precisionK(listResults[i,:], k)
    
    return valSum / listResults.shape[0]

def recallK(results, k):
    """
    This function computes the recall@k for a query
    giving the positive results
    Parameters
    ----------
    results : numpy array
        Array with 1 when retrive was positive, 0 otherwise.
    k : int
        k value to compute.
    Returns
    -------
    float
        r@k value.
    """
    
    return np.sum(results[:k])/np.sum(results)

def mRecallK(listResults, k):
    """
    This function computes the mean recall@k over all the queries.
    Parameters
    ----------
    listResults : numpy array
        For each query (row), 1 if retrieve was positive 0 otherwise.
    k : int
        k value to compute.
    Returns
    -------
    float
        Mean r@k value.
    """
    
    
    valSum = 0
    
    for i in range(listResults.shape[0]):
        valSum += recallK(listResults[i,:], k)
    
    return valSum / listResults.shape[0]
    
def averagePrecision(results):
    """
    This function computes the average precision for a query
    giving the positive results
    Parameters
    ----------
    results : numpy array
        Array with 1 when retrive was positive, 0 otherwise.
    Returns
    -------
    float
        ap value.
    """
    
    
    ap = (np.cumsum(results) * results)/(np.array(range(results.shape[0])) + 1)
    
    if np.sum(results) == 0:
        return 0
    
    return np.sum(ap)/np.sum(results)

def MAP(listResults):
    """
    This function computes the mean average previcision over all the queries.
    Parameters
    ----------
    listResults : numpy array
        For each query (row), 1 if retrieve was positive 0 otherwise.
    Returns
    -------
    float
        Mean ap value.
    """
    
    valSum = 0
    
    for i in range(listResults.shape[0]):
        valSum += averagePrecision(listResults[i,:])
    
    return valSum / listResults.shape[0]

def precisionRecall(listResults):
    """
    This function computes the mean precision and recall of all queries.
    Parameters
    ----------
    listResults : numpy array
        For each query (row), 1 if retrieve was positive 0 otherwise.
    Returns
    -------
    numpy array, numpy array
        Mean precision and recall values
    """
    values = (np.array(range(listResults.shape[1])) + 1)
    values = values[np.newaxis, ...]
    p = np.cumsum(listResults, axis=1)/values
    positiveSum = (np.sum(listResults,axis = 1))
    positiveSum = positiveSum[:,np.newaxis]+1e-10
    r = np.cumsum(listResults, axis=1)/positiveSum 
    
                                    
    mp = np.mean(p, axis=0)
    mr = np.mean(r, axis=0)

    
    return mp, mr


def pk(actual, predicted, k=10):
    """
    Computes the precision at k.
    This function computes the precision at k between the query image and a list
    of database retrieved images.
    Parameters
    ----------
    actual : int
             The element that has to be predicted
    predicted : list
                A list of predicted elements (order does matter)
    k : int, optional
        The maximum number of predicted elements
    Returns
    -------
    score : double
            The precision at k over the input
    """
    if len(predicted) > k:
        predicted = predicted[:k]
    score = 0
    for i in range(len(predicted)):
        if actual == predicted[i]:
            score += 1
    
    return score / len(predicted)

def mpk(actual, predicted, k=10):
    """
    Computes the precision at k.
    This function computes the mean precision at k between a list of query images and a list
    of database retrieved images.
    Parameters
    ----------
    actual : list
             The query elements that have to be predicted
    predicted : list
                A list of predicted elements (order does matter) for each query element
    k : int, optional
        The maximum number of predicted elements
    Returns
    -------
    score : double
            The precision at k over the input
    """
    pk_list = []
    for i in range(len(actual)):
        score = pk(actual[i], predicted[i], k)
        pk_list.append(score)
    return np.mean(pk_list)